"""RGFU port from the verified 20260920 prototype (source SHA256 in catalog).

Only RGB-guided upsampling is retained; the historical wavelet alternative is
archived separately. Pinned VGGT DPT commit: a288dd0f14786c93483e45524328726ab7b1b4ce.
"""
from __future__ import annotations
import torch
from torch import nn
from torch.nn import functional as F

def _axis_indices_weights(n, m, *, device, dtype, align_corners):
    if min(n, m) < 1:
        raise ValueError('interpolation dimensions must be positive')
    index = torch.arange(m, device=device, dtype=dtype)
    if align_corners:
        pos = index * ((n-1)/(m-1) if m > 1 else 0.)
    else:
        pos = ((index+.5)*(n/m)-.5).clamp_min(0)
    lo = pos.floor().long().clamp(max=n-1)
    hi = (lo+1).clamp(max=n-1)
    fraction = pos-lo.to(dtype)
    return lo, hi, fraction


def guided_bilinear(feature, logits, *, align_corners=True):
    """Four neighbors; original bilinear weight times exp(logit), normalized.

    Use an algebraically equivalent delta from F.interpolate. Identical logits
    then produce a bit-exact original forward without a gradient-disabling branch.
    Subtracting the maximum keeps exponentiation stable and preserves zero base
    weights. No four-neighbor/channel stack is materialized.
    """
    if (feature.ndim != 4 or logits.ndim != 4 or logits.shape[:2] != (feature.shape[0], 4)
            or feature.device != logits.device):
        raise ValueError('feature NCHW and logits N4HW on the same device are required')
    if not torch.isfinite(logits).all():
        raise FloatingPointError('nonfinite RGB guidance logits')
    size = logits.shape[-2:]
    work_dtype = torch.float64 if feature.dtype == torch.float64 else torch.float32
    y0, y1, fy = _axis_indices_weights(feature.shape[-2], size[0], device=feature.device,
                                     dtype=work_dtype, align_corners=align_corners)
    x0, x1, fx = _axis_indices_weights(feature.shape[-1], size[1], device=feature.device,
                                     dtype=work_dtype, align_corners=align_corners)
    fy, fx = fy[:, None], fx[None, :]
    w = torch.stack(((1-fy)*(1-fx), (1-fy)*fx, fy*(1-fx), fy*fx))[None]
    delta = logits.to(work_dtype)
    active_delta = delta.masked_fill(w == 0, -torch.inf)
    scaled = w * torch.exp(active_delta-active_delta.amax(dim=1, keepdim=True))
    corrected = scaled / scaled.sum(dim=1, keepdim=True)
    # At exact boundaries inactive neighbors remain exactly inactive.
    difference = corrected-w/w.sum(dim=1, keepdim=True)
    out = F.interpolate(feature, size=size, mode='bilinear', align_corners=align_corners)
    for k, (ys, xs) in enumerate(((y0,x0), (y0,x1), (y1,x0), (y1,x1))):
        neighbor = feature[:, :, ys[:, None], xs[None, :]]
        out = out + neighbor * difference[:, k:k+1].to(feature.dtype)
    return out


class RGBGuidedUpsample(nn.Module):
    def __init__(self):
        super().__init__()
        self.predict = nn.Sequential(nn.Conv2d(3,32,3,padding=1), nn.ReLU(), nn.Conv2d(32,4,1))
        nn.init.zeros_(self.predict[-1].weight)
        nn.init.zeros_(self.predict[-1].bias)

    def forward(self, feature, rgb):
        return guided_bilinear(feature, self.predict(rgb), align_corners=True)


class RGFUHead(nn.Module):
    """Pinned DPT path with only the explicitly selected modification.

    Upstream _forward_impl corresponds to VGGT a288dd0. Retain its chunking,
    position embeddings, feature fusion, output activation and confidence. Never patch a module global.
    """
    def __init__(self, base, *, initialization_seed=700):
        super().__init__()
        self.base = base
        if base.feature_only or base.down_ratio != 1 or base.patch_size != 14:
            raise ValueError('RGFU requires the original dense depth DPT contract')
        if not isinstance(base.scratch.output_conv2[2], nn.Conv2d) or base.scratch.output_conv2[2].in_channels != 32:
            raise ValueError('unexpected final DPT output feature')
        # Model initialization must not move caller/data random streams.
        with torch.random.fork_rng(devices=[]):
            torch.random.default_generator.manual_seed(initialization_seed)
            self.extra = RGBGuidedUpsample()

    def forward(self, tokens, images, patch_start_idx, frames_chunk_size=8):
        if images.shape[-2:] != (518,518):
            raise ValueError('RGFU is fixed to 518x518')
        count = images.shape[1]
        chunk = count if frames_chunk_size is None else frames_chunk_size
        if chunk <= 0:
            raise ValueError('frames_chunk_size must be positive')
        results = [self._chunk(tokens, images[:,start:start+chunk], patch_start_idx, start, start+chunk)
                   for start in range(0,count,chunk)]
        return tuple(torch.cat([item[k] for item in results],dim=1) for k in (0,1))

    def _chunk(self, tokens, images, patch_start, start, end):
        from vggt.heads.head_act import activate_head
        head = self.base
        b,s,_,h,w = images.shape
        features = []
        for i, layer in enumerate(head.intermediate_layer_idx):
            x = tokens[layer][:,start:end,patch_start:]
            x = head.norm(x.reshape(b*s,-1,x.shape[-1]))
            x = x.permute(0,2,1).reshape(b*s,x.shape[-1],h//head.patch_size,w//head.patch_size)
            x = head.projects[i](x)
            if head.pos_embed:
                x = head._apply_pos_embed(x,w,h)
            features.append(head.resize_layers[i](x))
        x = head.scratch_forward(features)
        x = self.extra(x, images.reshape(b*s,3,h,w))
        if head.pos_embed:
            x = head._apply_pos_embed(x,w,h)
        x = head.scratch.output_conv2[1](head.scratch.output_conv2[0](x))
        raw = head.scratch.output_conv2[2](x)
        depth, confidence = activate_head(raw,activation=head.activation,conf_activation=head.conf_activation)
        return depth.reshape(b,s,*depth.shape[1:]), confidence.reshape(b,s,*confidence.shape[1:])

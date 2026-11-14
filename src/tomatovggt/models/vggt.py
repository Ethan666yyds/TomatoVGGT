"""VGGT depth wrapper resources; external upstream code and weights are required."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import torch
from torch import nn

from tomatovggt._io import sha256_file
from .lora import inject_lora


def validate_vendor(root: Path, expected_commit: str) -> None:
    commit = subprocess.check_output(['git', '-C', str(root), 'rev-parse', 'HEAD'], text=True).strip()
    dirty = subprocess.check_output(['git', '-C', str(root), 'status', '--porcelain', '--untracked-files=no'], text=True).strip()
    if commit != expected_commit or dirty:
        raise ValueError('VGGT source commit mismatch or tracked local modifications')


class DepthAdapter(nn.Module):
    """Wrap the upstream aggregator and depth head, with optional camera output."""

    def __init__(self, net: nn.Module):
        super().__init__()
        self.net = net

    def forward(self, images: torch.Tensor, include_camera: bool = False) -> dict:
        if images.ndim != 4:
            raise ValueError('expected one scene [views,3,height,width]')
        tokens, patch_start = self.net.aggregator(images[None])
        # Match the pinned upstream VGGT forward: autocast only the aggregator.
        with torch.autocast(device_type=images.device.type, enabled=False):
            depth, confidence = self.net.depth_head(tokens, images[None], patch_start)
            result = {'depth': depth[0, ..., 0].float(), 'depth_conf': confidence[0].float()}
            if include_camera:
                from vggt.utils.pose_enc import pose_encoding_to_extri_intri
                pose = self.net.camera_head(tokens)[-1]
                extrinsic, intrinsic = pose_encoding_to_extri_intri(pose, images.shape[-2:])
                result.update(extrinsic=extrinsic[0].float(), intrinsic=intrinsic[0].float())
        return result


def load_base_state_dict(checkpoint: Path) -> dict:
    """Identify safetensors after cache symlinks resolve to extensionless blobs."""
    with checkpoint.open('rb') as handle:
        prefix = handle.read(9)
    header_bytes = int.from_bytes(prefix[:8], 'little')
    safetensors_header = (len(prefix) == 9 and prefix[8:9] == b'{'
                          and 2 <= header_bytes <= min(100_000_000, checkpoint.stat().st_size - 8))
    if checkpoint.suffix == '.safetensors' or safetensors_header:
        from safetensors.torch import load_file
        weights = load_file(str(checkpoint), device='cpu')
    else:
        weights = torch.load(checkpoint, map_location='cpu', weights_only=True)
    if not isinstance(weights, dict) or not all(isinstance(v, torch.Tensor) for v in weights.values()):
        raise ValueError('base checkpoint must be an original flat VGGT state_dict')
    return weights


def load_vggt(vendor_root: Path, checkpoint: Path, checkpoint_sha256: str,
              vendor_commit: str, *, device: str = 'cuda', rank: int = 16,
              alpha: int = 32, rgfu: bool = False) -> DepthAdapter:
    validate_vendor(vendor_root, vendor_commit)
    if sha256_file(checkpoint) != checkpoint_sha256:
        raise ValueError('base checkpoint SHA256 mismatch')
    sys.path.insert(0, str(vendor_root))
    from vggt.models.vggt import VGGT
    net = VGGT(enable_camera=True, enable_depth=True, enable_point=False, enable_track=False)
    weights = load_base_state_dict(checkpoint)
    wanted = net.state_dict()
    extras = set(weights) - set(wanted)
    if set(wanted) - set(weights) or any(not k.startswith(('point_head.', 'track_head.')) for k in extras):
        raise ValueError('base state_dict has incompatible parameter names')
    net.load_state_dict({k: weights[k] for k in wanted}, strict=True)
    del weights
    if rgfu:
        if vendor_commit != 'a288dd0f14786c93483e45524328726ab7b1b4ce':
            raise ValueError('RGFU requires the verified VGGT DPT source revision')
        from .rgfu import RGFUHead
        net.depth_head = RGFUHead(net.depth_head)
    for parameter in net.parameters():
        parameter.requires_grad_(False)
    for parameter in net.depth_head.parameters():
        parameter.requires_grad_(True)
    injected = inject_lora(net.aggregator, r=rank, alpha=alpha, skip_first_n_blocks=4)
    if not injected:
        raise ValueError('no q/v LoRA modules injected')
    return DepthAdapter(net).to(device)


def parameter_groups(model: nn.Module, head_lr: float, lora_lr: float) -> list[dict]:
    head, lora = [], []
    for name, parameter in model.named_parameters():
        if parameter.requires_grad:
            (lora if 'lora_' in name else head).append(parameter)
    if not head or not lora:
        raise ValueError('expected both depth-head and LoRA trainable parameters')
    return [{'params': head, 'lr': head_lr}, {'params': lora, 'lr': lora_lr}]

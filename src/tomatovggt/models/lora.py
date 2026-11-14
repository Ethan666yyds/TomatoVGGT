"""Self-contained query/value LoRA for VGGT fused attention projections."""
from __future__ import annotations

import math
import torch
from torch import nn


class LoRAQKV(nn.Module):
    """Add low-rank updates to query/value slices; leave the key slice unchanged."""

    def __init__(self, base: nn.Linear, r: int = 16, alpha: int = 32):
        super().__init__()
        out_f, in_f = base.weight.shape
        assert out_f % 3 == 0, f"qkv 输出维应是 3 的倍数,得到 {out_f}"
        self.base = base
        for p in self.base.parameters():
            p.requires_grad_(False)

        self.dim = out_f // 3
        self.r = r
        self.scale = alpha / r
        # A: 共享下投影;B: 分别投到 q 段与 v 段
        self.lora_A = nn.Parameter(torch.empty(r, in_f))
        self.lora_B_q = nn.Parameter(torch.zeros(self.dim, r))
        self.lora_B_v = nn.Parameter(torch.zeros(self.dim, r))
        nn.init.kaiming_uniform_(self.lora_A, a=math.sqrt(5))
        # B 初始化为 0 → 训练开始时等价于原模型(不扰动预训练行为)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        out = self.base(x)
        low = torch.nn.functional.linear(x, self.lora_A)          # (..., r)
        dq = torch.nn.functional.linear(low, self.lora_B_q) * self.scale
        dv = torch.nn.functional.linear(low, self.lora_B_v) * self.scale
        out = out.clone()
        out[..., : self.dim] += dq                                 # q 段
        out[..., 2 * self.dim:] += dv                              # v 段
        return out


def inject_lora(
    model: nn.Module,
    target_substrings: tuple[str, ...] = ("frame_blocks", "global_blocks"),
    suffix: str = "attn.qkv",
    r: int = 16,
    alpha: int = 32,
    skip_first_n_blocks: int = 4,
) -> list[str]:
    """Replace matching fused qkv layers, excluding the first configured blocks."""
    injected: list[str] = []
    for name, module in list(model.named_modules()):
        if not name.endswith(suffix):
            continue
        if not any(t in name for t in target_substrings):
            continue
        # 形如 aggregator.frame_blocks.3.attn.qkv → 取块序号
        parts = name.split(".")
        try:
            blk = int(parts[parts.index("attn") - 1])
        except (ValueError, IndexError):
            blk = 999
        if blk < skip_first_n_blocks:
            continue

        parent = model.get_submodule(name.rsplit(".", 1)[0])
        child_name = name.rsplit(".", 1)[1]
        base = getattr(parent, child_name)
        setattr(parent, child_name, LoRAQKV(base, r=r, alpha=alpha))
        injected.append(name)
    return injected

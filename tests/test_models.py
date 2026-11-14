"""Verify upstream head precision while running the aggregator under autocast."""
import unittest
import tempfile
from pathlib import Path
import torch
from torch import nn
from tomatovggt.models.vggt import DepthAdapter, load_base_state_dict

class ProbeAggregator(nn.Module):
    def forward(self, images):
        self.autocast_enabled = torch.is_autocast_enabled('cpu')
        return images.float(), 0

class ProbeHead(nn.Module):
    def __init__(self):
        super().__init__()
        self.projection = nn.Conv2d(3, 1, 1)
    def forward(self, tokens, images, patch_start):
        self.autocast_enabled = torch.is_autocast_enabled('cpu')
        value = self.projection(tokens.flatten(0, 1)).reshape(1, images.shape[1], *images.shape[-2:])
        return value[..., None], torch.ones_like(value)

class AdapterPrecisionTests(unittest.TestCase):
    def test_safetensors_blob_after_symlink_resolution_and_torch_checkpoint(self):
        from safetensors.torch import save_file
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            weights = {'weight': torch.arange(6.).reshape(2, 3)}
            blob = root / ('a' * 64)
            save_file(weights, str(blob))
            link = root / 'model.safetensors'
            link.symlink_to(blob)
            self.assertTrue(torch.equal(load_base_state_dict(link.resolve())['weight'], weights['weight']))
            saved = root / 'base.pt'
            torch.save(weights, saved)
            self.assertTrue(torch.equal(load_base_state_dict(saved)['weight'], weights['weight']))

    def test_aggregator_autocast_and_upstream_fp32_head_match(self):
        torch.manual_seed(11)
        net = nn.Module()
        net.aggregator, net.depth_head = ProbeAggregator(), ProbeHead()
        adapter = DepthAdapter(net)
        images = torch.randn(2, 3, 4, 4)
        expected = net.depth_head.projection(images)[:, 0]
        with torch.autocast('cpu', dtype=torch.bfloat16):
            actual = adapter(images)['depth']
        self.assertTrue(net.aggregator.autocast_enabled)
        self.assertFalse(net.depth_head.autocast_enabled)
        self.assertEqual(actual.dtype, torch.float32)
        self.assertTrue(torch.equal(actual, expected))
        actual.sum().backward()
        self.assertTrue(torch.isfinite(net.depth_head.projection.weight.grad).all())


class LoRATests(unittest.TestCase):
    def test_zero_initialization_and_query_value_only_updates(self):
        from tomatovggt.models.lora import LoRAQKV
        torch.manual_seed(2)
        base = nn.Linear(4, 12)
        inputs = torch.randn(2, 4)
        expected = base(inputs).detach()
        layer = LoRAQKV(base, r=2, alpha=4)
        self.assertTrue(torch.equal(layer(inputs), expected))
        self.assertFalse(any(parameter.requires_grad for parameter in base.parameters()))
        with torch.no_grad():
            layer.lora_B_q.fill_(.2)
            layer.lora_B_v.fill_(.3)
        actual = layer(inputs)
        self.assertTrue(torch.equal(actual[:, 4:8], expected[:, 4:8]))
        self.assertFalse(torch.equal(actual[:, :4], expected[:, :4]))
        self.assertFalse(torch.equal(actual[:, 8:], expected[:, 8:]))
        actual.sum().backward()
        self.assertIsNone(base.weight.grad)
        self.assertTrue(torch.isfinite(layer.lora_A.grad).all())

    def test_injection_respects_block_selection(self):
        from tomatovggt.models.lora import inject_lora, LoRAQKV
        model = nn.Module()
        model.frame_blocks = nn.ModuleList([nn.Module() for _ in range(3)])
        for block in model.frame_blocks:
            block.attn = nn.Module()
            block.attn.qkv = nn.Linear(4, 12)
        injected = inject_lora(model, r=2, alpha=4, skip_first_n_blocks=2)
        self.assertEqual(injected, ['frame_blocks.2.attn.qkv'])
        self.assertIsInstance(model.frame_blocks[0].attn.qkv, nn.Linear)
        self.assertIsInstance(model.frame_blocks[2].attn.qkv, LoRAQKV)

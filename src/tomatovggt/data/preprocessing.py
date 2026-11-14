"""Explicit-view RGB preprocessing and owned CPU snapshots."""
from __future__ import annotations
from pathlib import Path
from typing import Any
import numpy as np
import torch
import torch.nn.functional as F
from PIL import Image

def select_cached_views(scene: dict[str, Any], view_ids: list[str]) -> dict[str, Any]:
    """Copy selected views from a validated, run-local CPU scene snapshot.

    Keep sampling outside this function so caching cannot consume RNG state.
    index_select owns its storage: augmenting a batch cannot corrupt the cache.
    Only fields already present in the snapshot are exposed to the caller.
    """
    if (not view_ids or len(set(view_ids)) != len(view_ids)
            or any(view not in scene['view_ids'] for view in view_ids)):
        raise ValueError('requested cached view IDs must be unique and present')
    indices = torch.tensor([scene['view_ids'].index(view) for view in view_ids])
    return {key: ((value.index_select(0, indices) if value.ndim and value.shape[0] == len(scene['view_ids']) else value.clone()) if isinstance(value, torch.Tensor)
                  else list(view_ids) if key == 'view_ids' else value)
            for key, value in scene.items()}

def preprocess_spec(resolution: int = 518, intermediate_resolution: int = 1024) -> dict[str, Any]:
    if resolution <= 0 or intermediate_resolution <= 0:
        raise ValueError("preprocessing resolutions must be positive")
    return {"id": "vggt-square-pil-bicubic-torch-bilinear-v1", "resolution": resolution,
            "intermediate_resolution": intermediate_resolution, "square_padding": "black_center_floor",
            "alpha_background": "white", "align_corners": False, "rgb_range": [0, 1],
            "pixel_coordinates": "edge_origin_centers_at_half_integer",
            "mask_resize": "nearest_direct", "spatial_valid": "input_support_intersect_optional_mask"}

def preprocess_image(image_path: str | Path, *, spatial_mask_path: str | Path | None = None,
                     resolution: int = 518, intermediate_resolution: int = 1024
                     ) -> dict[str, torch.Tensor]:
    preprocess_spec(resolution, intermediate_resolution)
    with Image.open(image_path) as opened:
        original = opened.copy()
    if original.mode == "RGBA":
        background = Image.new("RGBA", original.size, (255, 255, 255, 255))
        original = Image.alpha_composite(background, original)
    original = original.convert("RGB")
    width, height = original.size
    side = max(width, height)
    left, top = (side - width) // 2, (side - height) // 2
    padded = Image.new("RGB", (side, side), 0)
    padded.paste(original, (left, top))
    intermediate = padded.resize((intermediate_resolution, intermediate_resolution), Image.Resampling.BICUBIC)
    array = np.asarray(intermediate).copy()
    tensor = torch.from_numpy(array).permute(2, 0, 1).to(torch.float32).div_(255)
    images = F.interpolate(tensor.unsqueeze(0), size=(resolution, resolution), mode="bilinear",
                           align_corners=False)[0]
    valid = np.ones((height, width), dtype=np.uint8)
    if spatial_mask_path is not None:
        with Image.open(spatial_mask_path) as mask_image:
            if mask_image.size != (width, height):
                raise ValueError("spatial mask dimensions do not match original RGB")
            mask = np.asarray(mask_image)
            if mask.ndim != 2:
                raise ValueError("spatial mask must be one channel")
            valid &= (mask > 0).astype(np.uint8)
    mask_square = Image.new("L", (side, side), 0)
    mask_square.paste(Image.fromarray(valid), (left, top))
    spatial_valid = torch.from_numpy(np.asarray(mask_square.resize(
        (resolution, resolution), Image.Resampling.NEAREST)).copy()).bool()
    scale = resolution / float(side)
    transform = torch.tensor([[scale, 0, left * scale], [0, scale, top * scale], [0, 0, 1]],
                             dtype=torch.float32)
    return {"images": images, "spatial_valid": spatial_valid, "pixel_transform": transform}

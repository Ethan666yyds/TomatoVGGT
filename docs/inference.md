# Calibrated-rig inference

The release contains the original Q/V LoRA, RGFU depth head and RGB preprocessing used by the selected update-1000 model. The portable adapter contains all 188 trained-parameter and buffer tensors, with exact equality to the original checkpoint. Optimizer, RNG state and training metadata are omitted. No retraining is required.

## Install

Use Python 3.10+ and install PyTorch for your CUDA version using the [PyTorch installation guide](https://pytorch.org/get-started/locally/). A CUDA device with BF16 support is recommended for the original inference precision. CPU FP32 is supported for functional verification and is substantially slower.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e .
git clone https://github.com/facebookresearch/vggt.git vendor/vggt
git -C vendor/vggt checkout a288dd0f14786c93483e45524328726ab7b1b4ce
```

The pinned upstream checkout must have no tracked modifications. Upstream VGGT source and base weights retain their upstream license; they are downloaded separately.

## Weights

Extract `tomatovggt_weights.zip` at the repository root. This creates `weights/tomatovggt.safetensors`, `weights/model.json` and a loading guide. Both the portable adapter and base weights are verified by SHA256 at load time.

Download the original base weights from the pinned revision:

```bash
python - <<'PY'
from huggingface_hub import hf_hub_download
path = hf_hub_download(
    repo_id='facebook/VGGT-1B',
    revision='860abec7937da0a4c03c41d3c269c366e82abdf9',
    filename='model.safetensors',
)
print(path)
PY
```

Base SHA256: `f164acf60724910d8fe1578bb499d800850c7bb0948db7555c413f9fbe60467e`.

## Run on one synthetic plant

After extracting `tomato3d_synthetic.zip`, use one plant's RGB images and calibrated cameras:

```bash
tomatovggt-infer \
  --images-dir datasets/tomato3d_synthetic/accepted/SYN_TOMATO_0201/rgb \
  --cameras datasets/tomato3d_synthetic/accepted/SYN_TOMATO_0201/cameras.json \
  --base-weights /path/to/model.safetensors \
  --output outputs/SYN_TOMATO_0201
```

For CPU verification add `--device cpu --threads 6`. The default input is exactly 15 views, in the order specified by `cameras.json`; `--expected-views` explicitly overrides that count for diagnostics. Output directories must be new, to preserve previous results.

Outputs:

- `prediction.npz`: 518×518 depth, confidence, calibrated intrinsics/extrinsics, view IDs and image-support masks.
- `point_cloud.ply`: a colored cloud in the coordinate frame of the supplied calibrated cameras. It includes every finite positive-depth pixel inside the unpadded image region; no plant-foreground segmentation or confidence filtering is applied. Optional `--point-stride N` subsamples pixels for viewing.
- `inference.json`: weight/input hashes, preprocessing, camera convention, scale, precision, point count and unwarmed forward time.

Calibration contains ordered `view_ids` and matching `views`. Each camera row has `camera_id`, raw-image intrinsics `K` (or the dataset's `K_raw`), and `T_world_to_camera` (3×4 or 4×4; translation in metres). Optional `width`/`height` must match the RGB image. The loader applies the same square-padding and resize transform to intrinsics as to images; dataset `K_518` values are checked when supplied.

## Interpretation

This model is adapted to the fixed TomatoWUR camera rig. The entry point uses provided calibrated cameras, without running the frozen predicted-camera head. It does not imply cross-platform generalization or comparable performance with predicted cameras.

Depth is camera-axis Z. The default `--depth-scale 1` keeps the model's native depth scale. An explicit positive scale can be supplied and is recorded. No reference depth/point cloud, median-depth scale alignment, ICP or Sim(3) is used during inference. Published geometry metrics use separate known-camera, reference-assisted scale protocols; this inference command alone does not reproduce those metrics. Raw clouds include background pixels unless separately segmented.

## Verify

```bash
VGGT_ROOT="$PWD/vendor/vggt" python -m unittest discover -s tests -v
```

The suite covers explicit image order, calibration transforms, half-pixel unprojection, PLY serialization, strict adapter loading, original LoRA behavior, RGFU interpolation and pinned upstream depth-head parity.

To reproduce the portable export from the original, hash-bound research checkpoint:

```bash
python scripts/export_inference_weights.py \
  --checkpoint /path/to/original/tomatovggt.pt \
  --output /path/to/new/weights
```

This exporter checks the original checkpoint hash before deserialization and verifies exact equality for every exported tensor. Ordinary inference only reads Safetensors.

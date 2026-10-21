# Downloads

[← Back to TomatoVGGT](../README.md#downloads)

Download archives are being prepared for the restricted [Tomato3D folder on Google Drive](https://zenodo.org/records/24221170). The folder currently has restricted access; an archive is not available until its upload has been verified.

## Data

| Archive | Contents | Status |
| :--- | :--- | :--- |
| `tomato3d_real.zip` | 44 TomatoWUR plants · 660 images | In preparation |
| `tomato3d_synthetic.zip` | 222 synthetic plants · 3,330 images | Upload pending |

The 200 synthetic training plants and 22 frozen-model evaluation plants share one archive. Their roles are recorded in the [fixed data split](../datasets/splits/main_benchmark.json). All views of a plant share its role. Real geometry is a reconstruction reference; synthetic geometry is ground truth.

See the [dataset guide](../datasets/README.md) for asset descriptions, provenance, and licensing.

## Model weights

| Archive | Contents | Status |
| :--- | :--- | :--- |
| `tomatovggt_weights.zip` | TomatoVGGT checkpoint and loading information | Upload pending |

The checkpoint requires the matching VGGT base weights and model structure. Model inference and training code are being prepared for release.

## Predictions and point clouds

| Archive | Contents | Status |
| :--- | :--- | :--- |
| `tomatovggt_results.zip` | Main experiment predictions and point clouds | Upload pending |

Lightweight [metrics and result tables](../results/README.md) are already included in this repository. Real and synthetic evaluations are summarized separately.

## Archive layout and verification

Extract each archive at the repository root:

```text
TomatoVGGT/
├── datasets/
│   ├── tomato3d_real/
│   └── tomato3d_synthetic/
├── weights/
└── results/
```

The [SHA256 checksum list](../checksums.sha256) records archive hashes. A checksum entry alone does not indicate upload completion.

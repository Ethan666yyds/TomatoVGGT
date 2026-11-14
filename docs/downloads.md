# Downloads

[← Back to TomatoVGGT](../README.md#downloads)

The fixed data split, plant-level metrics, result tables, summary script, and portable inference code are included in this repository. Data, weights and prediction archives are being prepared in a [Zenodo draft](https://zenodo.org/deposit/24221170). Reserved DOI: `10.5281/zenodo.24221170` (not yet activated). Public download links will be added after licensing and publication metadata are finalized and the record is published.

## Data

| Archive | Contents | Status |
| :--- | :--- | :--- |
| TomatoWUR source data | 44 real plants · 660 images | [Original provider](https://github.com/WUR-ABE/TomatoWUR); not redistributed in this upload |
| `tomato3d_synthetic.zip` | 222 synthetic plants · 3,330 images; sanitized metadata | Prepared for Zenodo |

The 200 synthetic training plants and 22 frozen-model evaluation plants share one archive. Their roles are recorded in the [fixed data split](../datasets/splits/main_benchmark.json). All views of a plant share its role. Real geometry is a reconstruction reference; synthetic geometry is ground truth.

See the [dataset guide](../datasets/README.md) for asset descriptions, provenance, and licensing.

## Model weights

| Archive | Contents | Status |
| :--- | :--- | :--- |
| `tomatovggt_weights.zip` | Portable Safetensors adapter and exact model/base bindings | Prepared for Zenodo |

The adapter requires the matching VGGT base weights and model structure. [Model inference](inference.md) is implemented and verified with a full 15-view forward pass. Training code is outside this release.

## Predictions and point clouds

| Archive | Contents | Status |
| :--- | :--- | :--- |
| `tomatovggt_results.zip` | Main experiment predictions and point clouds, original bytes | Prepared for Zenodo |

Lightweight [metrics and result tables](../results/README.md) are already included in this repository. The paper’s 32-plant summary and separate real and synthetic summaries are provided.

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

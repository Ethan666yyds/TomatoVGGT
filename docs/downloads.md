# Downloads

[← Back to TomatoVGGT](../README.md#downloads)

Data, model weights, predictions, and point clouds are **coming soon**. Download links will be added on this page after the archives are uploaded and verified. The fixed data split, plant-level metrics, result tables, and summary script are already available in this repository.

## Data

| Archive | Contents | Status |
| :--- | :--- | :--- |
| `tomato3d_real.zip` | 44 TomatoWUR plants · 660 images | Coming soon |
| `tomato3d_synthetic.zip` | 222 synthetic plants · 3,330 images | Coming soon |

The 200 synthetic training plants and 22 frozen-model evaluation plants share one archive. Their roles are recorded in the [fixed data split](../datasets/splits/main_benchmark.json). All views of a plant share its role. Real geometry is a reconstruction reference; synthetic geometry is ground truth.

See the [dataset guide](../datasets/README.md) for asset descriptions, provenance, and licensing.

## Model weights

| Archive | Contents | Status |
| :--- | :--- | :--- |
| `tomatovggt_weights.zip` | TomatoVGGT checkpoint and loading information | Coming soon |

The checkpoint requires the matching VGGT base weights and model structure. Model inference and training code are being prepared for release.

## Predictions and point clouds

| Archive | Contents | Status |
| :--- | :--- | :--- |
| `tomatovggt_results.zip` | Main experiment predictions and point clouds | Coming soon |

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

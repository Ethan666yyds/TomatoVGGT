# Downloads

[← Back to TomatoVGGT](../README.md#downloads)

The fixed data split, plant-level metrics, result tables, summary script, and portable inference code are included in this repository. Data, weights, prediction archives and the licensing bundle are hosted in the [Zenodo release](https://zenodo.org/records/24221170), DOI [10.5281/zenodo.24221170](https://doi.org/10.5281/zenodo.24221170).

## Data

| Archive | Contents | Status |
| :--- | :--- | :--- |
| TomatoWUR source data | 44 real plants · 660 images | [Original provider](https://github.com/WUR-ABE/TomatoWUR); not redistributed in this upload |
| `tomato3d_synthetic.zip` | 222 synthetic plants · 3,330 images; original generated content CC BY-NC 4.0; calibration CC BY-SA 4.0 | [Zenodo](https://zenodo.org/records/24221170) |

The 200 synthetic training plants and 22 frozen-model evaluation plants share one archive. Their roles are recorded in the [fixed data split](../datasets/splits/main_benchmark.json). All views of a plant share its role. Real geometry is a reconstruction reference; synthetic geometry is ground truth.

See the [dataset guide](../datasets/README.md) for asset descriptions, provenance, and licensing.

### Numbered archive parts

Large archives are stored as numbered 128 MiB parts, allowing parallel transfers and recovery after interruption. Each part is an ordinary Zenodo file. A part cannot be extracted by itself. The [download manifest](../download_manifest.json) records every part's size and SHA256, and the original combined ZIP SHA256.

Download and reconstruct the data/model/result archives and obtain the accompanying license bundle with Python 3.10+ (standard library only):

```bash
python restore_archives.py --download --directory downloads
```

Reruns skip valid downloaded parts. To combine parts already downloaded manually, omit `--download`. Public downloads require no token. Extract the restored ZIP archives and `tomatovggt_licenses.zip` at the repository root. The archive-root release notice and license map define the current terms; earlier preparation READMEs retained inside payload subtrees are historical provenance.

## Model weights

| Archive | Contents | Status |
| :--- | :--- | :--- |
| `tomatovggt_weights.zip` | Portable Safetensors adapter and exact model/base bindings | [Zenodo](https://zenodo.org/records/24221170) |

The adapter requires the matching VGGT base weights and model structure. [Model inference](inference.md) is implemented and verified with a full 15-view forward pass. Training code is outside this release.

The selected original VGGT-1B checkpoint and adapted weights retain CC BY-NC 4.0. They are not the separately licensed commercial VGGT checkpoint. Code and data have their own component-specific terms; see the [license map](../LICENSE.md).

## Predictions and point clouds

| Archive | Contents | Status |
| :--- | :--- | :--- |
| `tomatovggt_results.zip` | Main experiment predictions and point clouds, original payload bytes | [Zenodo](https://zenodo.org/records/24221170) |

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

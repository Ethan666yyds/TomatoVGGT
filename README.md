<h1 align="center">TomatoVGGT</h1>

<p align="center">
  <strong>Fast 3D plant reconstruction on calibrated multi-camera phenotyping platforms</strong><br>
  Parameter-efficient adaptation of VGGT, validated on tomato.
</p>

<p align="center">
  <a href="#overview">Overview</a> &nbsp;·&nbsp;
  <a href="#tomato3d">Tomato3D</a> &nbsp;·&nbsp;
  <a href="#downloads">Downloads</a> &nbsp;·&nbsp;
  <a href="#quick-start">Quick start</a> &nbsp;·&nbsp;
  <a href="results/README.md">Results</a>
</p>

---

## Overview

TomatoVGGT is a tomato-adapted VGGT model for a fixed, calibrated multi-camera phenotyping platform. Adaptation learns metric depth that is consistent across views, enabling feed-forward reconstruction from the platform's 15 RGB images. Experiments use the public TomatoWUR platform and its calibration.

- **Parameter-efficient adaptation** — jointly updates attention Q/V LoRA parameters and the full depth head while keeping the original backbone weights frozen; approximately 2.98% of parameters in the enabled components are trainable.
- **Thin-structure enhancement** — RGB-Guided Feature Upsampling (RGFU) and Thin-Structure Geometric Loss (TSGL) target slender organs and organ boundaries.
- **Synthetic–Real Joint Training (SRJT)** — combines real observations and synthetic plants rendered with the platform's camera calibration in Tomato3D.

Adaptation takes about 2 hours on one RTX 4090; reconstruction takes about 1 second per plant. The reconstructions support 3DGS initialization and measurements of internode length and phyllotactic angle with reference-skeleton assistance. The released checkpoint is tied to this imaging platform; another platform or crop requires re-adaptation.

[Paper overview and reported experiments](docs/paper.md) &nbsp;·&nbsp; [Evaluation protocol](docs/evaluation.md)

<p align="center">
  <a href="docs/images/pipeline.png">
    <img src="docs/images/pipeline.png" alt="Tomato3D construction and train/validation/test split; parameter-efficient VGGT adaptation; 3D reconstruction and phenotypic measurement." width="680">
  </a>
  <br>
  <sub>TomatoVGGT pipeline · Click the figure to view at full resolution.</sub>
</p>

## Tomato3D

**266 plants · 3,990 images · 15 views per plant**

Tomato3D brings together real observations from TomatoWUR and synthetic tomato plants.

| Component | Plants | Images | Split |
| :--- | ---: | ---: | :--- |
| **TomatoWUR** · real | 44 | 660 | 28 train / 6 validation / 10 retrospective test |
| **Synthetic** | 222 | 3,330 | 200 train / 22 frozen-model evaluation |

Training uses 228 plants (28 real + 200 synthetic). Six real validation plants are used for checkpoint selection. The paper's test set contains **32 plants** (10 real retrospective test plants + 22 synthetic frozen-model evaluation plants).

All views of a plant share one split. Real geometry is a **reconstruction reference**; synthetic geometry is **ground truth**.

[Dataset guide](datasets/README.md) &nbsp;·&nbsp; [Fixed data split](datasets/splits/main_benchmark.json)

## Downloads

Release materials are hosted on [Zenodo](https://doi.org/10.5281/zenodo.24221170). This repository includes the fixed data split, plant-level metrics, result tables, summary script and portable inference code. Large archives use verified numbered parts and an automatic download/reconstruction tool.

| Resource | Availability |
| :--- | :--- |
| [Synthetic data](docs/downloads.md#data) | [Zenodo release](https://zenodo.org/records/24221170) |
| [Real data](docs/real_data.md) | Original TomatoWUR provider |
| [Model weights](docs/downloads.md#model-weights) | [Zenodo release](https://zenodo.org/records/24221170) |
| [Predictions and point clouds](docs/downloads.md#predictions-and-point-clouds) | [Zenodo release](https://zenodo.org/records/24221170) |
| [Metrics and result tables](results/README.md) | Included in this repository |

[Package guide](docs/downloads.md) &nbsp;·&nbsp; [SHA256 checksums](checksums.sha256)

```bash
python restore_archives.py --download --directory downloads
```

The tool verifies every part and reconstructed archive. See the package guide for extraction and the [real-data guide](docs/real_data.md) for official source data and preprocessing.

## Quick start

Reproduce the main result tables with **Python 3.10+**. Only the standard library is required.

```bash
git clone https://github.com/Ethan666yyds/TomatoVGGT.git
cd TomatoVGGT

# Paper Table 2 · 10 real + 22 synthetic plants
python scripts/summarize_results.py --dataset tomato3d

# Real plants · 10 retrospective test plants
python scripts/summarize_results.py --dataset tomatowur

# Synthetic plants · 22 frozen-model evaluation plants
python scripts/summarize_results.py --dataset tomato_synth_validation
```

<details>
<summary><strong>Save full-precision means and Markdown tables</strong></summary>

Pass an output directory to save both formats:

```bash
python scripts/summarize_results.py --dataset tomato3d --output-dir results/tables/tomato3d
python scripts/summarize_results.py --dataset tomatowur --output-dir results/tables/tomatowur
python scripts/summarize_results.py --dataset tomato_synth_validation --output-dir results/tables/tomato_synth_validation
```

</details>

### Model inference

Portable inference code and Safetensors adapter loading are included. Install the package, obtain the matching VGGT base weights, and supply the 15 RGB views and calibrated rig cameras. See the [inference guide](docs/inference.md) for installation, exact weight/source revisions, a runnable example and verification.

The inference command writes depth maps, a colored PLY cloud and input/model provenance. The adapter requires the matching VGGT base weights. Inference uses the model's native depth scale. Paper Tables 2 and 4 use separate per-plant reference-assisted scale alignment; Table 3 also evaluates native scale. Training and full metric reproduction are outside this inference release.

See the [result records](results/README.md) and [evaluation protocol](docs/evaluation.md) for metric definitions, known-camera and scale-assisted conditions, and source records.

## Acknowledgements and license

TomatoVGGT builds on [VGGT](https://github.com/facebookresearch/vggt). The real component of Tomato3D comes from [TomatoWUR](https://github.com/WUR-ABE/TomatoWUR) and retains its [CC BY-SA 4.0 data license](https://creativecommons.org/licenses/by-sa/4.0/). See the [dataset guide](datasets/README.md) for attribution and component licensing.

Licenses apply by component: independently authored software uses MIT; VGGT-derived code retains the VGGT License; the adapted model weights retain CC BY-NC 4.0; original synthetic data uses CC BY-NC 4.0; released results and documentation use CC BY-SA 4.0, and upstream calibration retains CC BY-SA 4.0. These are component-specific terms. See [LICENSE.md](LICENSE.md), [NOTICE.md](NOTICE.md) and [CITATION.cff](CITATION.cff) for the exact scope, attribution and citation.

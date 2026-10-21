<h1 align="center">TomatoVGGT</h1>

<p align="center">
  <strong>Feed-forward 3D reconstruction of tomato plants</strong><br>
  Parameter-efficient adaptation of VGGT for fine plant structures.
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

TomatoVGGT jointly updates attention Q/V LoRA parameters and the full depth head while keeping the original backbone weights frozen, training approximately 2.98% of the parameters in the enabled model components. It combines three components for fine-structure reconstruction:

- **RGFU · RGB-Guided Feature Upsampling** — uses RGB guidance during feature upsampling.
- **TSGL · Thin-Structure Geometric Loss** — combines thin-structure depth weighting with local normal consistency.
- **SRJT · Synthetic–Real Joint Training** — learns jointly from synthetic and real plant observations.

<p align="center">
  <a href="docs/images/pipeline.png">
    <img src="docs/images/pipeline.png" alt="TomatoVGGT pipeline: dataset construction, joint training, and downstream reconstruction workflow." width="680">
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

The paper calls the **38 non-training plants** (16 real + 22 synthetic) its test set. Six real plants are used for checkpoint selection; the reported evaluation covers the remaining **32 plants** (10 real + 22 synthetic).

All views of a plant share one split. Real geometry is a **reconstruction reference**; synthetic geometry is **ground truth**.

[Dataset guide](datasets/README.md) &nbsp;·&nbsp; [Fixed data split](datasets/splits/main_benchmark.json)

## Downloads

| Resource | Availability |
| :--- | :--- |
| [Real and synthetic data](docs/downloads.md#data) | Real data in preparation; synthetic upload pending |
| [Model weights](docs/downloads.md#model-weights) | Upload pending |
| [Predictions and point clouds](docs/downloads.md#predictions-and-point-clouds) | Upload pending |
| [Metrics and result tables](results/README.md) | Included in this repository |

[Package guide](docs/downloads.md) &nbsp;·&nbsp; [Tomato3D on Google Drive](https://zenodo.org/records/24221170) &nbsp;·&nbsp; [SHA256 checksums](checksums.sha256)

The Drive folder currently has restricted access. Download availability will be updated after upload verification.

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

Model inference, training, and evaluation from predictions are being prepared for release. The TomatoVGGT checkpoint requires the matching VGGT base weights.

See the [result records](results/README.md) and [evaluation protocol](docs/evaluation.md) for metric definitions, known-camera and scale-assisted conditions, and source records.

## Acknowledgements and license

TomatoVGGT builds on [VGGT](https://github.com/facebookresearch/vggt). The real component of Tomato3D comes from [TomatoWUR](https://github.com/WUR-ABE/TomatoWUR) and retains its [CC BY-SA 4.0 data license](https://creativecommons.org/licenses/by-sa/4.0/). See the [dataset guide](datasets/README.md) for attribution and component licensing.

# TomatoVGGT

TomatoVGGT adapts VGGT for fine-structure reconstruction of tomato plants, combining RGB-Guided Feature Upsampling (RGFU), Thin-Structure Geometric Loss (TSGL), and Synthetic–Real Joint Training (SRJT).

## Pipeline

![TomatoVGGT pipeline](docs/images/pipeline.png)

## Tomato3D

Tomato3D combines real observations from TomatoWUR with synthetic tomato plants: **244 plants and 3,660 images** in total.

| Component | Plants | Images | Use |
|---|---:|---:|---|
| TomatoWUR | 44 | 660 | 28 training, 6 validation, 10 retrospective test |
| TomatoSynth-200 | 200 | 3,000 | Training |

All views of a plant belong to the same split. Real geometry is a reconstruction reference; synthetic geometry is ground truth.

[Dataset description](datasets/README.md) · [Data split](datasets/splits/main_benchmark.json)

| Resource | File | Download |
|---|---|---|
| Synthetic data | `tomato_synth_200.zip` | In preparation |
| TomatoWUR data | `tomatowur.zip` | In preparation |
| Model weights | `weights.zip` | In preparation |
| Predictions and point clouds | `results.zip` | In preparation |

## Installation and Usage

The main-table summary requires **Python 3.10+** and the standard library.

```bash
git clone https://github.com/Ethan666yyds/TomatoVGGT.git
cd TomatoVGGT
python scripts/summarize_results.py
```

To save the full-precision means and Markdown table:

```bash
python scripts/summarize_results.py --output-dir results/tables
```

Model inference, training, and evaluation from predictions are being prepared for release. The TomatoVGGT checkpoint requires the matching VGGT base weights.

## Sources and License

TomatoVGGT builds on [VGGT](https://github.com/facebookresearch/vggt). The real component of Tomato3D comes from [TomatoWUR](https://github.com/WUR-ABE/TomatoWUR), which retains its [CC BY-SA 4.0 data license](https://creativecommons.org/licenses/by-sa/4.0/).

Source records and metric definitions are described in the [results documentation](results/README.md) and [evaluation protocol](docs/evaluation.md).

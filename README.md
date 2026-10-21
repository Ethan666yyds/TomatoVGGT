# TomatoVGGT

TomatoVGGT adapts VGGT for fine-structure reconstruction of tomato plants, combining RGB-Guided Feature Upsampling (RGFU), Thin-Structure Geometric Loss (TSGL), and Synthetic–Real Joint Training (SRJT).

## Pipeline

![TomatoVGGT pipeline](docs/images/pipeline.png)

## Tomato3D

Tomato3D combines real observations from TomatoWUR with synthetic tomato plants: **266 plants and 3,990 images** in total.

| Component | Plants | Images | Use |
|---|---:|---:|---|
| TomatoWUR | 44 | 660 | 28 training, 6 validation, 10 retrospective test |
| Tomato3D synthetic | 222 | 3,330 | 200 training, 22 frozen-model evaluation |

All views of a plant belong to the same split. Real geometry is a reconstruction reference; synthetic geometry is ground truth.

[Dataset description](datasets/README.md) · [Data split](datasets/splits/main_benchmark.json)

| Resource | File | Download |
|---|---|---|
| Real data | `tomato3d_real.zip` | In preparation |
| Synthetic data | `tomato3d_synthetic.zip` | Upload pending |
| Model weights | `tomatovggt_weights.zip` | Upload pending |
| Main experiment predictions and point clouds | `tomatovggt_results.zip` | Upload pending |

The 200 training and 22 evaluation synthetic plants share one archive. Their roles are recorded in the data split. Download archives are currently being prepared for restricted Google Drive access. [Archive checksums](checksums.sha256) are available; a checksum entry alone does not indicate upload completion.

## Installation and Usage

The main-table summary requires **Python 3.10+** and the standard library.

```bash
git clone https://github.com/Ethan666yyds/TomatoVGGT.git
cd TomatoVGGT
python scripts/summarize_results.py --dataset tomatowur
python scripts/summarize_results.py --dataset tomato_synth_validation
```

To save the full-precision means and Markdown table:

```bash
python scripts/summarize_results.py --dataset tomatowur --output-dir results/tables/tomatowur
python scripts/summarize_results.py --dataset tomato_synth_validation --output-dir results/tables/tomato_synth_validation
```

Model inference, training, and evaluation from predictions are being prepared for release. The TomatoVGGT checkpoint requires the matching VGGT base weights.

## Sources and License

TomatoVGGT builds on [VGGT](https://github.com/facebookresearch/vggt). The real component of Tomato3D comes from [TomatoWUR](https://github.com/WUR-ABE/TomatoWUR), which retains its [CC BY-SA 4.0 data license](https://creativecommons.org/licenses/by-sa/4.0/).

Source records and metric definitions are described in the [results documentation](results/README.md) and [evaluation protocol](docs/evaluation.md).

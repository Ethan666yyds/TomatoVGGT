# Main experiment results

Six methods (VGGT, Pi3X, DA3, Fast3R, MASt3R and TomatoVGGT) are evaluated on 10 real and 22 synthetic plants. The two datasets are summarized separately, with equal weight per plant.

| Dataset | Plant-level records | Summary |
|---|---|---|
| TomatoWUR | [60 records](metrics/tomatowur/per_plant.json) | [Table](tables/tomatowur/main_results.md) · [Full precision](tables/tomatowur/main_results.json) |
| Tomato3D synthetic | [132 records](metrics/tomato_synth_validation/per_plant.json) | [Table](tables/tomato_synth_validation/main_results.md) · [Full precision](tables/tomato_synth_validation/main_results.json) |

Records retain original metric values and source SHA256 identifiers. The synthetic comparison includes the later completed MASt3R results. Real geometry is a reconstruction reference; synthetic geometry is ground truth.

```bash
python scripts/summarize_results.py --dataset tomatowur --output-dir results/tables/tomatowur
python scripts/summarize_results.py --dataset tomato_synth_validation --output-dir results/tables/tomato_synth_validation
```

`tomatovggt_results.zip` contains all 192 original predictions, the 10 existing TomatoVGGT real-plant PLY files, and all 132 synthetic point clouds. Archive predictions and clouds retain original bytes. Synthetic metric record copies replace the original machine-specific prediction path with the package-relative path; numeric values stay unchanged. Results from ablations, external evaluation and 3DGS are excluded.

See the [evaluation protocol](../docs/evaluation.md) for the known-camera and scale-assisted conditions and the retrospective real split.

# Evaluation

The main comparison includes VGGT, Pi3X, DA3, Fast3R, MASt3R, and TomatoVGGT on the same 10 TomatoWUR plants, with 15 input views per plant. Metrics are computed per plant, then averaged with equal weight.

## Geometry and depth

For predicted points P and reconstruction-reference points R:

- **Accuracy**: mean nearest-neighbour distance from P to R.
- **Completeness**: mean nearest-neighbour distance from R to P.
- **Chamfer distance**: the mean of Accuracy and Completeness.
- **F-score@5 mm**: the harmonic mean of precision and recall at a 5 mm distance threshold. Stored values are fractions; tables display percentages.
- **AbsRel**: mean absolute relative depth error over valid plant pixels, after per-plant scale alignment.

Distance metrics are reported in millimetres. Whole-plant geometry includes semantic labels 1, 2, and 4; stem geometry includes labels 2 and 4. Support poles, label 3, are excluded from the reconstruction reference.

Evaluation uses reference intrinsics and extrinsics. A single scale is computed as the median ratio of reference depth to predicted depth over common valid plant pixels across all views of a plant. Depth is back-projected using the reference cameras. Camera-axis depth and reference coordinates use metres.

Geometry uses at most 300,000 predicted points, sampled at uniform intervals. The main protocol does not apply ICP, an additional Sim(3) fit, confidence-based point filtering, or post-hoc bounding-box cropping. Methods retain their original preprocessing and input resolutions.

## Data split and checkpoint

TomatoWUR contains 28 training plants, 6 validation plants, and 10 retrospective test plants. All 44 plants have historical reported metrics, and historical holdout plants were used during development. The test set is therefore reported as retrospective.

All 200 synthetic plants are used for training. The synthetic source package's original split is retained as source metadata; the project split is given in [main_benchmark.json](../datasets/splits/main_benchmark.json).

The TomatoVGGT checkpoint was selected by the lowest whole-plant CD on the 6 validation plants. The selected checkpoint is from optimizer update 1,000.

## Result files

[per_plant.json](../results/metrics/per_plant.json) contains the nine main metrics for each of the 60 method–plant pairs. Original numeric precision is retained. Historical baseline fields are mapped to the shared field names, including the historical method key `pi3` to `pi3x`.

[summarize_results.py](../scripts/summarize_results.py) regenerates the table from these records. It summarizes stored metrics; it does not rerun model inference or recompute geometry from predictions.

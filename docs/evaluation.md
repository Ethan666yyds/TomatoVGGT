# Evaluation

The main comparison includes VGGT, Pi3X, DA3, Fast3R, MASt3R, and TomatoVGGT on the same 32 test plants: 10 real TomatoWUR plants and 22 synthetic plants, with 15 input views per plant. Metrics are computed per plant, then averaged with equal weight. Paper Table 2 pools all 32 plants; the repository also retains separate domain summaries. MASt3R uses pairwise inference followed by global alignment optimization; the other models use a single forward pass.

## Geometry and depth

For predicted points P and geometry points R (real reconstruction references or synthetic ground truth):

- **Accuracy**: mean nearest-neighbour distance from P to R.
- **Completeness**: mean nearest-neighbour distance from R to P.
- **Chamfer distance**: the mean of Accuracy and Completeness.
- **F5 (F-score@5 mm)**: the harmonic mean of precision and recall at a 5 mm distance threshold. Stored values are fractions; tables display percentages.
- **AbsRel**: mean absolute relative depth error over valid plant pixels, after per-plant scale alignment.

Distance metrics are reported in millimetres. Whole-plant geometry includes semantic labels 1, 2, and 4; stem geometry includes labels 2 and 4. Support poles, label 3, are excluded from the reconstruction reference.

The main comparison (Table 2) and ablations (Table 4) use reference intrinsics and extrinsics. A single scale is computed as the median ratio of reference depth to predicted depth over common valid plant pixels across all 15 views of a plant. Depth is back-projected using the reference cameras and half-integer pixel centers `(u + 0.5, v + 0.5)`. Extrinsics are world-to-camera. Camera-axis depth and reference coordinates use metres.

Geometry uses at most 300,000 predicted points, sampled at uniform intervals. The main protocol does not apply ICP, an additional Sim(3) fit, confidence-based point filtering, or post-hoc bounding-box cropping. Methods retain their original preprocessing and input resolutions.

## Data split and checkpoint

TomatoWUR contains 28 training plants, 6 validation plants, and 10 retrospective test plants. All 44 plants have historical reported metrics, and historical holdout plants were used during development. The test set is therefore reported as retrospective.

All 200 synthetic plants are used for training. The synthetic source package's original split is retained as source metadata; the project split is given in [main_benchmark.json](../datasets/splits/main_benchmark.json).

The paper's test set contains 32 plants: 10 real and 22 synthetic. The six real validation plants are used for checkpoint selection within this fixed split and are excluded from the test-set tables. Historical-development exposure of the real plants remains documented in the split file.

The TomatoVGGT checkpoint was selected by the lowest whole-plant CD on the 6 validation plants. The selected checkpoint is from optimizer update 1,000.

## Depth-scale experiment (paper Table 3)

Table 3 compares three settings on the same 32 plants, retaining reference cameras and the geometric scoring protocol:

- **No alignment:** use the model's native predicted depths.
- **Per-plant alignment:** one reference-assisted median depth scale across all views, as in Table 2.
- **Per-view alignment:** a separate reference-assisted scale for each of the 15 views.

The reported global scale factor is the plant-wise mean of the factors multiplying predicted depth. Per-view scale variation is the standard deviation of a plant's 15 scale factors relative to its global factor, then averaged across plants. See the [paper overview](paper.md#depth-scale-and-cross-view-consistency-table-3) for the reported values. Native-scale evaluation still uses reference cameras, valid plant regions and reference geometry for scoring; it is distinct from exporting an unsegmented raw inference cloud.

## Result files

[per_plant.json](../results/metrics/tomatowur/per_plant.json) contains the nine main metrics for each of the 60 method–plant pairs. Original numeric precision is retained. Historical baseline fields are mapped to the shared field names, including the historical method key `pi3` to `pi3x`.

[summarize_results.py](../scripts/summarize_results.py) regenerates the table from these records. It summarizes stored metrics; it does not rerun model inference or recompute geometry from predictions.

## Synthetic evaluation

The additional 22 plants were evaluated with frozen model weights and were not used for training or model selection. All six methods cover the same plants and all 15 views. Synthetic geometry is ground truth. Scoring uses the recorded known-camera, global plant median depth-scale protocol and jointly visible surfaces, without ICP, Sim(3) or confidence clipping. The nine metric definitions and units match those above, and separate domain summaries remain available.

[132 synthetic records](../results/metrics/tomato_synth_validation/per_plant.json) preserve all metric values and source hashes. Run `python scripts/summarize_results.py --dataset tomato_synth_validation` to reproduce their table.

## Paper Table 2

Run `python scripts/summarize_results.py --dataset tomato3d` to reproduce the paper's 32-plant main comparison from the 60 real and 132 synthetic method–plant records. Each method uses the same 10 real and 22 synthetic plants. The six checkpoint-selection plants are excluded.

Each plant has weight 1/32: the combined mean equals `(10 × real_mean + 22 × synthetic_mean) / 32`, using full-precision values. It is not an equal average of the two domain means. F-scores remain fractions until display. The combined JSON retains the domain-specific plant IDs, geometry reference kinds, protocols, and source hashes.

[Combined table](../results/tables/tomato3d/main_results.md) · [Full precision](../results/tables/tomato3d/main_results.json)

## Downstream experiments

The 3DGS comparison (Table 5) evaluates the **input views used for optimization**. It uses reference cameras, reference-assisted scale alignment and foreground support. Each metric is first averaged over 15 views, then equally over successfully reconstructed plants: 29 for COLMAP initialization and 32 each for VGGT and TomatoVGGT initialization. It is not a held-out novel-view evaluation.

Trait evaluation uses organ-level pairs: 203 internodes from 28 plants (6 real, 22 synthetic) and 188 phyllotactic angles from 26 plants (4 real, 22 synthetic). Attachment locations use reference-skeleton assistance, with manual checks for real plants. Reference values are manual measurements for real plants and generated ground truth for synthetic plants. Angle error is the circular difference in `[-180°, 180°)`; MAPE excludes zero reference values, and the reported R² is squared Pearson correlation. See the [reported experiments and release scope](paper.md#phenotypic-measurement-figure-7).

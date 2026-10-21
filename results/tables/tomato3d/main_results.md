# TomatoVGGT main results

32 Tomato3D plants; equal arithmetic mean across plants. Best values are bold.

| Method | Whole CD ↓ (mm) | Whole Accuracy ↓ (mm) | Whole Completeness ↓ (mm) | Whole F-score@5 mm ↑ (%) | Stem CD ↓ (mm) | Stem Accuracy ↓ (mm) | Stem Completeness ↓ (mm) | Stem F-score@5 mm ↑ (%) | AbsRel ↓ |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| VGGT | 24.463 | 45.309 | 3.617 | 20.93 | 36.046 | 68.228 | 3.865 | 18.59 | 0.09035 |
| Pi3X | 23.549 | 43.268 | 3.830 | 22.22 | 33.410 | 63.307 | 3.513 | 21.93 | 0.09029 |
| DA3 | 41.495 | 79.654 | 3.336 | 19.05 | 80.846 | 158.326 | 3.366 | 15.17 | 0.13139 |
| Fast3R | 47.883 | 82.753 | 13.014 | 9.79 | 61.908 | 107.280 | 16.535 | 5.88 | 0.15284 |
| MASt3R | 93.350 | 180.680 | 6.020 | 8.23 | 98.857 | 190.403 | 7.310 | 5.75 | 0.25013 |
| TomatoVGGT | **5.204** | **8.842** | **1.566** | **61.62** | **5.915** | **10.306** | **1.525** | **59.17** | **0.02185** |

Paper Table 2: 10 real + 22 synthetic plants, with each plant weighted 1/32. The six real plants used for checkpoint selection are excluded. The 38-plant non-training cohort shown as the test set in the paper includes those six plants. Separate domain summaries and source hashes are retained in the JSON.

Distances are measured against real reconstruction references and synthetic ground truth, using known cameras and one plant-wide median depth scale across all views. No ICP or Sim(3) is applied.

CD = (Accuracy + Completeness) / 2. F-score uses a 5 mm threshold. AbsRel is measured over valid overlapping plant pixels after scale alignment. JSON retains full precision; F-scores are fractions in JSON and percentages in this table.

TomatoVGGT uses update 1000 selected by validation CD on six real validation plants. All 44 have historical reported metrics; 14 holdout plants have been used for development evaluation. This is a retrospective test split, not an unseen final test.

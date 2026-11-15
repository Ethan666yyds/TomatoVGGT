# TomatoVGGT main results

10 TomatoWUR plants; equal arithmetic mean across plants. Best values are bold.

| Method | Whole CD ↓ (mm) | Whole Accuracy ↓ (mm) | Whole Completeness ↓ (mm) | Whole F-score@5 mm ↑ (%) | Stem CD ↓ (mm) | Stem Accuracy ↓ (mm) | Stem Completeness ↓ (mm) | Stem F-score@5 mm ↑ (%) | AbsRel ↓ |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| VGGT | 21.930 | 39.893 | 3.968 | 25.91 | 30.418 | 57.098 | 3.737 | 22.42 | 0.10307 |
| Pi3X | 21.882 | 39.150 | 4.615 | 23.12 | 29.711 | 54.570 | 4.851 | 16.50 | 0.10238 |
| DA3 | 29.262 | 54.390 | 4.134 | 19.06 | 39.274 | 74.639 | 3.909 | 14.34 | 0.12119 |
| Fast3R | 36.416 | 59.665 | 13.168 | 13.74 | 48.550 | 80.731 | 16.368 | 7.33 | 0.14345 |
| MASt3R | 74.085 | 143.048 | 5.122 | 12.95 | 80.146 | 153.792 | 6.500 | 7.52 | 0.22371 |
| TomatoVGGT | **6.510** | **10.809** | **2.211** | **58.54** | **7.938** | **13.783** | **2.092** | **51.39** | **0.03006** |

Distances are measured against the published reconstruction reference, using known cameras and one plant-wide median depth scale across all views. No ICP or Sim(3) is applied.

CD = (Accuracy + Completeness) / 2. F-score uses a 5 mm threshold. AbsRel is measured over valid overlapping plant pixels after scale alignment. JSON retains full precision; F-scores are fractions in JSON and percentages in this table.

MASt3R uses pairwise inference followed by global alignment optimization; the other models use a single forward pass.

TomatoVGGT uses update 1000 selected by validation CD on six real validation plants. All 44 have historical reported metrics; 14 holdout plants have been used for development evaluation. This is a retrospective test split, not an unseen final test.

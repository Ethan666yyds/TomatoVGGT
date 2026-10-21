# TomatoVGGT main results

22 Tomato3D synthetic plants; equal arithmetic mean across plants. Best values are bold.

| Method | Whole CD ↓ (mm) | Whole Accuracy ↓ (mm) | Whole Completeness ↓ (mm) | Whole F-score@5 mm ↑ (%) | Stem CD ↓ (mm) | Stem Accuracy ↓ (mm) | Stem Completeness ↓ (mm) | Stem F-score@5 mm ↑ (%) | AbsRel ↓ |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| VGGT | 25.615 | 47.772 | 3.458 | 18.66 | 38.605 | 73.286 | 3.923 | 16.85 | 0.08457 |
| Pi3X | 24.306 | 45.140 | 3.473 | 21.81 | 35.091 | 67.278 | 2.905 | 24.40 | 0.08479 |
| DA3 | 47.056 | 91.138 | 2.974 | 19.04 | 99.742 | 196.366 | 3.118 | 15.54 | 0.13602 |
| Fast3R | 53.096 | 93.247 | 12.944 | 8.00 | 67.979 | 119.348 | 16.611 | 5.22 | 0.15711 |
| MASt3R | 102.106 | 197.785 | 6.428 | 6.09 | 107.361 | 207.045 | 7.678 | 4.94 | 0.26214 |
| TomatoVGGT | **4.610** | **7.948** | **1.273** | **63.02** | **4.996** | **8.725** | **1.267** | **62.70** | **0.01812** |

Distances are measured against synthetic ground truth, using known cameras and one plant-wide median depth scale across all views. No ICP or Sim(3) is applied.

CD = (Accuracy + Completeness) / 2. F-score uses a 5 mm threshold. AbsRel is measured over valid overlapping plant pixels after scale alignment. JSON retains full precision; F-scores are fractions in JSON and percentages in this table.

TomatoVGGT uses update 1000 selected by validation CD on six real validation plants. Not used for training or model selection; model frozen before evaluation.

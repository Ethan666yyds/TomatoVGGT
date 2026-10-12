# Tomato3D

Tomato3D combines 44 real TomatoWUR plants with 200 synthetic plants. Each plant has 15 views, giving 244 plant identities and 3,660 images.

| Component | Geometry | Training | Validation | Retrospective test |
|---|---|---:|---:|---:|
| TomatoWUR | Reconstruction reference | 28 | 6 | 10 |
| TomatoSynth-200 | Synthetic ground truth | 200 | 0 | 0 |

The [project split](splits/main_benchmark.json) assigns all views of each plant to one subset. The synthetic source package retains its original 160/20/20 split metadata; this experiment uses all 200 synthetic plants for training.

## Files

The data archives are being prepared. The expected extraction locations are:

```text
datasets/
├── tomato_synth_200/
├── tomatowur/
└── splits/
    └── main_benchmark.json
```

The real component contains RGB images, camera parameters, semantic annotations, reconstruction-reference point clouds, and point labels. The synthetic component contains RGB images, camera parameters, depth, semantic labels, and synthetic geometry.

TomatoWUR keeps its original plant identifiers, attribution, and [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) data license. See the [original dataset repository](https://github.com/WUR-ABE/TomatoWUR) and [dataset DOI](https://doi.org/10.4121/e2c59841-4653-45de-a75e-4994b2766a2f).

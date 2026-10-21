# Tomato3D

Tomato3D contains 44 real plants from TomatoWUR and 222 synthetic plants, with 15 views per plant: **266 plant identities and 3,990 images**.

| Component | Geometry | Training | Model-selection validation | Reported evaluation |
|---|---|---:|---:|---:|
| Real / TomatoWUR | Reconstruction reference | 28 | 6 | 10 retrospective test |
| Synthetic | Ground truth | 200 | 0 | 22 frozen-model evaluation |

All views of a plant share its role in the [project split](splits/main_benchmark.json). The original synthetic source metadata retains historical 160/20/20 labels; this project used all original 200 plants for training. The additional 22 plants were generated and evaluated after model freezing, without training or model selection. They are not the six real validation plants used to choose the checkpoint.

## Relation to the paper

The paper and pipeline call the 38 non-training plants (16 real + 22 synthetic) the **test set**. Of these, six real plants are used for checkpoint selection. The reported geometric evaluation uses the remaining **32 plants: 10 real + 22 synthetic**. Training covers 228 plants (28 real + 200 synthetic).

The fixed split records actual roles: `real.val` contains the six selection plants, `real.test` contains the ten retrospective evaluation plants, and `synthetic.eval` contains the 22 frozen-model evaluation plants. The paper's 38-plant cohort is their union; its 32-plant evaluation subset excludes `real.val`. No plant IDs or selection roles are reassigned.

## Downloads and layout

Data downloads are coming soon. Links will be added to the [download guide](../docs/downloads.md#data) once ready. The planned real archive is `tomato3d_real.zip`; the single synthetic archive is `tomato3d_synthetic.zip`. Extract each at the repository root:

```text
datasets/
├── tomato3d_real/
├── tomato3d_synthetic/
│   ├── accepted/<plant_id>/
│   ├── main_benchmark.json
│   └── provenance/
└── splits/main_benchmark.json
```

The real package is being prepared from the original experiment inputs. The planned contents are RGB, cameras, semantic annotations, reference clouds and point labels. Synthetic assets include RGB, cameras, depth and semantic supervision, Blender scenes, meshes, visible and full surfaces, skeletons and traits. Package manifests verify distributed files; historical source manifests in provenance may describe larger source deliveries.

TomatoWUR retains original sample identities, attribution and its [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) data license. See the [source repository](https://github.com/WUR-ABE/TomatoWUR) and [dataset DOI](https://doi.org/10.4121/e2c59841-4653-45de-a75e-4994b2766a2f). Calibration in the synthetic data also retains its upstream source. Original synthetic-data licensing will be finalized before the data download is released.

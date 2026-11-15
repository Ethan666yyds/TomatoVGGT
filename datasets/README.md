# Tomato3D

Tomato3D contains 44 real plants from TomatoWUR and 222 synthetic plants, with 15 views per plant: **266 plant identities and 3,990 images**.

| Component | Geometry | Training | Model-selection validation | Reported evaluation |
|---|---|---:|---:|---:|
| Real / TomatoWUR | Reconstruction reference | 28 | 6 | 10 retrospective test |
| Synthetic | Ground truth | 200 | 0 | 22 frozen-model evaluation |

All views of a plant share its role in the [project split](splits/main_benchmark.json). The original synthetic source metadata retains historical 160/20/20 labels; this project used all original 200 plants for training. The additional 22 plants were generated and evaluated after model freezing, without training or model selection. They are not the six real validation plants used to choose the checkpoint.

## Relation to the paper

Six real validation plants are used for checkpoint selection. The reported geometric evaluation uses **32 plants: 10 real retrospective test plants + 22 synthetic frozen-model evaluation plants**. Training covers 228 plants (28 real + 200 synthetic).

The fixed split records actual roles: `real.val` contains the six selection plants, `real.test` contains the ten retrospective evaluation plants, and `synthetic.eval` contains the 22 frozen-model evaluation plants. The 32-plant test set excludes `real.val`. No plant IDs or selection roles are reassigned.

## Downloads and layout

The synthetic archive is hosted in the [Zenodo release](https://zenodo.org/records/24221170), with download and reconstruction instructions in the [download guide](../docs/downloads.md#data). The single synthetic archive is `tomato3d_synthetic.zip`. Extract it at the repository root:

```text
datasets/
├── tomato3d_real/
├── tomato3d_synthetic/
│   ├── accepted/<plant_id>/
│   ├── main_benchmark.json
│   └── provenance/
└── splits/main_benchmark.json
```

Real data should be obtained from the original TomatoWUR provider; they are not redistributed in this upload. Synthetic assets include RGB, cameras, depth and semantic supervision, Blender scenes, meshes, visible and full surfaces, skeletons and traits. Package manifests verify distributed files; historical source manifests in provenance may describe larger source deliveries.

The synthetic release removes PNG text/EXIF metadata, Blender file-browser directory buffers and local absolute paths in runtime metadata. All 3,330 images retain identical decoded pixels; all 222 scenes retain identical geometry and camera parameters and were opened in Blender for verification. Numeric geometry/supervision and generation seeds are unchanged. Cache lineage RGB hashes are updated to the sanitized image hashes. `manifest.sha256` describes the distributed copy; `sanitization.json` inventories edits.

Original synthetic images, geometry and generated supervision use [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/) for noncommercial reuse. Released result assets and documentation use CC BY-SA 4.0. The component-specific rights and attribution are identified in [LICENSE.md](../LICENSE.md) and [NOTICE.md](../NOTICE.md). TomatoWUR retains original sample identities, attribution and its CC BY-SA 4.0 data license. See the [source repository](https://github.com/WUR-ABE/TomatoWUR) and [dataset DOI](https://doi.org/10.4121/e2c59841-4653-45de-a75e-4994b2766a2f). Calibration in the synthetic data retains its upstream source and applicable terms. The [real-data guide](../docs/real_data.md) documents download, fixed roles and RGB preprocessing.

# TomatoWUR source data and preprocessing

## Obtain the original data

Download TomatoWUR from its [official dataset DOI](https://doi.org/10.4121/e2c59841-4653-45de-a75e-4994b2766a2f). Use the [source repository](https://github.com/WUR-ABE/TomatoWUR) for the provider's directory descriptions and utilities. Original RGB images and reconstruction references are not redistributed in the Tomato3D synthetic release.

The data license is CC BY-SA 4.0; the provider's GitHub software is separately GPL-3.0 licensed. Retain the dataset authors, DOI, license and source identities. See [NOTICE.md](../NOTICE.md) for attribution. Geometry from the real dataset is a **reconstruction reference**, rather than exact synthetic ground truth.

## Select the fixed plant identities

The authoritative list is [datasets/splits/main_benchmark.json](../datasets/splits/main_benchmark.json):

- `real.train`: 28 plants, used for training.
- `real.val`: 6 plants, used for checkpoint selection.
- `real.test`: 10 plants, used for retrospective reported evaluation.

All 15 views of a plant retain its role. The historical-development exposure and retrospective split interpretation are recorded in the same file; this is not a newly collected unseen test set. Select files by the complete original `Harvest_*_PotNr_*` identity, without reassigning plant IDs or moving validation plants into the evaluation cohort.

The research inputs use the provider's `0-paper-2Dto3D_improved` annotation source. When reproducing an annotation-dependent analysis, use the matching original annotations and reconstruction references, and record the source download/version and hashes. The portable RGB inference path does not require those annotations or reference geometry.

## RGB preprocessing and cameras

The released implementation is `tomatovggt.data.preprocessing.preprocess_image`:

1. Convert RGB inputs to RGB; alpha, when present, is composited over white.
2. Center the original image in a black square whose side is the longer original dimension; integer padding uses floor placement.
3. Resize the square to 1024×1024 with PIL bicubic interpolation.
4. Convert to float RGB in [0,1] and resize to 518×518 with PyTorch bilinear interpolation, `align_corners=False`.
5. Preserve a support mask so padded pixels are excluded from cloud export.

Apply the same square-padding and resize pixel transform to the original intrinsic matrix. Keep calibrated world-to-camera poses in the original coordinate frame, with translations in metres. Use explicit, matching view IDs for RGB images and cameras. The inference command verifies ordering, image/calibration sizes, valid pinhole intrinsics, rotations and supplied `K_518` values when present.

For raw image dimensions W×H, side S=max(W,H), left=floor((S-W)/2), top=floor((S-H)/2), the transform is:

```text
A = [[518/S, 0,     left*518/S],
     [0,     518/S, top*518/S ],
     [0,     0,     1         ]]
K_518 = A @ K_original
```

This project uses half-integer pixel centers and camera-axis Z depth. The standalone command consumes raw-image `K` (or dataset `K_raw`) plus `T_world_to_camera` and applies the image transform itself. See the [inference guide](inference.md) for the camera JSON schema and a runnable example.

## Evaluation scope

The inference command uses provided calibrated cameras and native model depth scale, without reference geometry or automatic scale alignment. The released Table 2 result records use known cameras and per-plant reference-assisted scale alignment. Paper Table 3 also compares native depths and per-view alignment, retaining reference geometry and foreground regions for scoring. Run the standard-library summary script to reproduce Table 2 and its domain summaries; do not treat standalone inference output as a newly reproduced paper metric. Full real-data training/evaluation preparation is outside this portable-inference release. See the [paper overview](paper.md) for downstream measurement conditions.

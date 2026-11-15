# Paper overview

**Adapting a 3D foundation model for fast and accurate plant reconstruction on multi-camera phenotyping platforms: a case study on tomato**

This guide summarizes the revised manuscript's method and experiments. TomatoVGGT is the model obtained by adapting VGGT to tomato observations from a fixed, calibrated multi-camera platform. Tomato3D combines public TomatoWUR observations with synthetic plants rendered using that platform's calibration.

## Method and data

The method has three contributions:

1. Parameter-efficient adaptation jointly trains attention Q/V LoRA parameters and the full depth head while freezing the original backbone weights. The aim is metric depth that is consistent across views under the platform's imaging conditions.
2. RGB-Guided Feature Upsampling (RGFU) and Thin-Structure Geometric Loss (TSGL) improve thin-organ and boundary reconstruction. TSGL combines region-weighted depth fitting with local predicted-normal consistency on valid, depth-continuous plant surfaces.
3. Synthetic–Real Joint Training (SRJT) balances the two domains, with synthetic geometry providing exact ground truth under the same camera calibration.

Tomato3D contains 266 plants and 3,990 images, with 15 views per plant. Training uses 28 real and 200 synthetic plants; validation uses 6 real plants for checkpoint selection; testing uses 10 real and 22 synthetic plants. The 32 test plants exclude the six validation plants. Real geometry is a reconstruction reference; synthetic geometry is ground truth. The real split remains retrospective, with historical-development exposure recorded in the [fixed split](../datasets/splits/main_benchmark.json). See the [dataset guide](../datasets/README.md).

TomatoWUR's public imaging system has 15 calibrated, synchronized RGB cameras at three heights, with five cameras around the plant at each height. The study uses this existing platform and its released calibration.

## Adaptation settings

| Setting | Configuration |
|---|---|
| Trainable parameters | 34,621,670; 2.9849% of parameters in enabled model components |
| Q/V LoRA | Block indices 4–23 in both within-view and cross-view attention; 40 locations; rank 16, alpha 32; shared down-projection within each layer |
| Depth head | Entire head trainable, including RGFU; original backbone and camera head frozen; point and tracking heads disabled |
| SRJT | Eight alternating microsteps per update, four real and four synthetic; four views of one plant per microstep; each loss divided by eight |
| Optimizer | AdamW; depth-head/RGFU learning rate 1e-4, LoRA 1e-5; weight decay 0.01; gradient norm clip 1.0 |
| Schedule and selection | 1,000 updates; cosine decay to zero without warm-up; validate every 100 updates on six real plants; minimum whole-plant CD, earlier checkpoint on ties; selected update 1,000 |
| TSGL | Thin-region weight 2.5, other valid regions 1; leaf-edge radius 2 pixels; thin-region confidence floor 1.5; log regularizer 0.2; normal weight 0.05; continuity threshold 0.02; epsilon 1e-8 |
| Precision and seed | BF16 aggregator, FP32 depth head; random seed 0 |
| Research environment | Python 3.11, PyTorch 2.5.1, CUDA 12.1; one RTX 4090 (24 GiB) |

There are 32 images contributing gradients to each optimizer update, but cross-view attention receives only four views of one plant in each training forward pass. Evaluation uses all 15 views. Adaptation takes about 2 hours and peaks at about 11.6 GB GPU memory; a 15-view reconstruction takes about 1 second on an RTX 4090. The portable release supports inference; it does not include the complete training pipeline.

## Main geometric comparison (Table 2)

The [main table](../results/tables/tomato3d/main_results.md) and [full-precision JSON](../results/tables/tomato3d/main_results.json) cover six methods on the same 32 test plants. They are regenerated from 192 released method–plant records with equal plant weights. TomatoVGGT achieves whole-plant CD of 5.204 mm and stem CD of 5.915 mm, compared with VGGT's 24.463 mm and 36.046 mm.

Table 2 and the ablation table use reference cameras, one reference-assisted median depth scale per plant across all views, and valid plant regions. There is no ICP, additional Sim(3) fitting or confidence filtering. MASt3R requires pairwise inference and global alignment optimization; the other compared models use a single forward pass. See the [evaluation protocol](evaluation.md) for definitions and aggregation.

## Depth scale and cross-view consistency (Table 3)

The last three columns report whole-plant CD in millimetres.

| Method | Global scale factor | Per-view scale variation | No alignment | Per-plant alignment | Per-view alignment |
|---|---|---|---|---|---|
| VGGT | 1.36 | 10.4% | 91.580 | 24.463 | 8.700 |
| TomatoVGGT | 1.00 | 0.6% | 5.408 | 5.204 | 4.955 |

These are equal-weight means over the same 32 plants. The global scale factor multiplies predicted depth. Per-view variation is the standard deviation of the 15 view-specific scale factors relative to the plant's global factor. Per-plant alignment is the Table 2 setting; per-view alignment requires reference depth for every view. No alignment preserves native predicted depth while retaining reference cameras, plant-region selection and geometry scoring.

TomatoVGGT's native-scale CD is 5.408 mm, close to its per-plant aligned value of 5.204 mm. This evidence concerns the evaluated platform. The raw cloud exported by the portable CLI also includes background pixels; exporting it alone does not reproduce these scores.

## Component ablations (Table 4)

| Variant | FT | RGFU | TSGL | SRJT | Whole plant CD ↓ (mm) | Whole plant Acc. ↓ (mm) | Whole plant Comp. ↓ (mm) | Whole plant F5 ↑ (%) | Stem CD ↓ (mm) | Stem Acc. ↓ (mm) | Stem Comp. ↓ (mm) | Stem F5 ↑ (%) | AbsRel ↓ |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| VGGT (pretrained) | — | — | — | — | 24.463 | 45.309 | 3.617 | 20.93 | 36.046 | 68.228 | 3.865 | 18.59 | 0.09035 |
| VGGT-FT | ✓ | — | — | — | 17.466 | 31.573 | 3.359 | 27.07 | 23.352 | 42.574 | 4.129 | 21.59 | 0.06522 |
| w/o RGFU | ✓ | — | ✓ | ✓ | 5.600 | 9.563 | 1.638 | 58.66 | 6.267 | 10.959 | 1.574 | 56.93 | 0.02312 |
| w/o TSGL | ✓ | ✓ | — | ✓ | **5.138** | **8.740** | **1.536** | 61.51 | 6.021 | 10.532 | **1.511** | 57.62 | **0.02177** |
| w/o SRJT | ✓ | ✓ | ✓ | — | 17.799 | 32.292 | 3.306 | 26.84 | 22.322 | 40.885 | 3.759 | 22.03 | 0.06529 |
| TomatoVGGT | ✓ | ✓ | ✓ | ✓ | 5.204 | 8.842 | 1.566 | **61.62** | **5.915** | **10.306** | 1.525 | **59.17** | 0.02185 |

Values are equal-weight plant means on the same 32 test plants. FT jointly fine-tunes the depth head and attention LoRA. VGGT-FT uses real data, original bilinear upsampling and the baseline depth objective. The baseline retains common-scale normalization, confidence-weighted residuals and logarithmic regularization, with unit regional weights and no thin-region confidence floor or normal term. Each removal keeps the other designs enabled; all fine-tuned configurations use the same optimizer-update budget.

SRJT has the largest effect among these component removals on the pooled test set. RGFU improves both whole-plant and stem metrics. TSGL improves stem CD and F5 while slightly increasing whole-plant CD and AbsRel; it does not improve every metric. Bold marks the best value in each column.

## 3DGS initialization (Table 5)

| Method | PSNR (dB) ↑ | SSIM ↑ | LPIPS ↓ |
|---|---|---|---|
| COLMAP + 3DGS | 24.5046 | 0.9272 | 0.1358 |
| VGGT + 3DGS | 32.1363 | 0.9746 | 0.0883 |
| TomatoVGGT + 3DGS | **32.2716** | **0.9754** | **0.0862** |

These are **input-view reconstruction** metrics under reference-assisted conditions. Average the 15 views within each plant, then equally average successful plants. COLMAP succeeds on 29 of 32 plants; VGGT and TomatoVGGT each cover all 32. The comparison does not measure held-out novel-view quality.

All configurations use the same Graphdeco backend, reference cameras, reference-assisted scale alignment and foreground support, a black background, image long side of 1,920 pixels, 7,000 optimization steps and spherical harmonics degree 3. The RGB objective is 0.8 L1 + 0.2 (1 − SSIM), without depth supervision. Each method retains its actual initialization density. TomatoVGGT improves PSNR over VGGT by 0.1353 dB; the improvement in these rendering metrics is small.

## Phenotypic measurement (Figure 7)

| Trait | Valid pairs | Plants | RMSE | MAPE | R² |
|---|---:|---|---:|---:|---:|
| Internode length | 203 | 28 (6 real + 22 synthetic) | 2.26 mm | 2.51% | 0.9861 |
| Phyllotactic angle | 188 | 26 (4 real + 22 synthetic) | 5.81° | 1.73% | 0.9632 |

Measurements use the 3DGS reconstructions. Reference skeletons assist in locating attachment regions; local main-stem and petiole axes are fitted there, with manual checks of real-plant correspondence and measurement locations. Reference trait values are manual measurements for real plants and generated ground truth for synthetic plants. Four real test plants lack manual trait values, and two more lack phyllotactic-angle values.

Internode length is the 3D distance between adjacent main-stem attachment nodes. Phyllotactic angle is the clockwise directed azimuth difference between adjacent petiole projections, mapped to [0°, 360°). Angular errors use circular differences in [−180°, 180°). Reported R² is squared Pearson correlation; MAPE uses nonzero reference values. This demonstrates reference-assisted trait measurement rather than a fully automatic organ-localization pipeline.

## Scope and available evidence

The method assumes fixed, calibrated cameras and repeated imaging on a phenotyping platform. The released TomatoVGGT checkpoint learns the scale and imaging conditions of the TomatoWUR rig. Re-adaptation is needed when the platform or crop changes; cross-platform and cross-crop performance has not been validated. Unknown-camera handheld capture is outside the evaluated setting.

The repository's [summary script](../scripts/summarize_results.py) reproduces Table 2 and separate domain tables from released plant-level metrics. Tables 3–5 and Figure 7 above are manuscript-reported summaries, not additional outputs of that script. The [release archive](downloads.md) includes the main-comparison predictions and specified point clouds, not complete ablation or 3DGS experiment artifacts. The [Zenodo DOI](https://doi.org/10.5281/zenodo.24221170) identifies the released resource collection; it is not an article DOI. Published archives remain a fixed release snapshot.

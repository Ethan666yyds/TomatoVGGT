# Main experiment results

The result records cover VGGT, Pi3X, DA3, Fast3R, MASt3R, and TomatoVGGT on the same 10 retrospective test plants.

| File | Contents |
|---|---|
| [metrics/per_plant.json](metrics/per_plant.json) | 60 method–plant records with the nine main metrics |
| [tables/main_results.json](tables/main_results.json) | Full-precision plant-wise means |
| [tables/main_results.md](tables/main_results.md) | Main comparison table |

Records are derived directly from the archived per-plant result files. Each record retains a source identifier and SHA256 digest. Method names and metric keys are normalized; the original metric values are preserved.

The prediction and point-cloud archive is being prepared separately as `results.zip`.

To regenerate the table, run from the repository root:

```bash
python scripts/summarize_results.py --output-dir results/tables
```

See the [evaluation protocol](../docs/evaluation.md) for metric definitions, reference-camera usage, scale alignment, and the retrospective split.

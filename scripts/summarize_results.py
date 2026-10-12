#!/usr/bin/env python3
"""Validate the fixed main benchmark records and reproduce its result table.

Requires only Python's standard library. The default command prints Markdown;
--output-dir writes main_results.json and main_results.md to that directory.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
METHODS = {
    "vggt": "VGGT",
    "pi3x": "Pi3X",
    "da3": "DA3",
    "fast3r": "Fast3R",
    "mast3r": "MASt3R",
    "tomatovggt": "TomatoVGGT",
}
GEOMETRY = ("chamfer_mm", "accuracy_mm", "completeness_mm", "f_score_5mm")
GROUPS = {"whole_plant": GEOMETRY, "stem": GEOMETRY, "depth": ("abs_rel",)}
COLUMNS = (
    ("whole_plant", "chamfer_mm", "Whole CD ↓ (mm)", 3, 1),
    ("whole_plant", "accuracy_mm", "Whole Accuracy ↓ (mm)", 3, 1),
    ("whole_plant", "completeness_mm", "Whole Completeness ↓ (mm)", 3, 1),
    ("whole_plant", "f_score_5mm", "Whole F-score@5 mm ↑ (%)", 2, 100),
    ("stem", "chamfer_mm", "Stem CD ↓ (mm)", 3, 1),
    ("stem", "accuracy_mm", "Stem Accuracy ↓ (mm)", 3, 1),
    ("stem", "completeness_mm", "Stem Completeness ↓ (mm)", 3, 1),
    ("stem", "f_score_5mm", "Stem F-score@5 mm ↑ (%)", 2, 100),
    ("depth", "abs_rel", "AbsRel ↓", 5, 1),
)


def _reject_constant(value: str):
    raise ValueError(f"non-finite JSON number: {value}")


def _read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"), parse_constant=_reject_constant)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _number(value, context: str, *, fraction: bool = False) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{context}: expected a number")
    if not math.isfinite(value) or value < 0 or (fraction and value > 1):
        raise ValueError(f"{context}: invalid metric value")
    return float(value)


def summarize(records_path: Path, split_path: Path) -> dict:
    payload, split = _read_json(records_path), _read_json(split_path)
    plants = split["real"]["test"]
    if (not isinstance(plants, list) or len(plants) != 10
            or any(not isinstance(p, str) or not p for p in plants)
            or len(set(plants)) != 10):
        raise ValueError("the main benchmark must contain 10 unique test plant IDs")
    other_plants = set(split["real"]["train"]) | set(split["real"]["val"])
    if set(plants) & other_plants:
        raise ValueError("test plant IDs overlap training or validation")
    exposure = split.get("historical_exposure")
    if not isinstance(exposure, str) or not exposure:
        raise ValueError("the retrospective test interpretation must be retained")
    if payload.get("dataset") != "TomatoWUR" or payload.get("split") != "test":
        raise ValueError("records must describe the TomatoWUR test split")
    if payload.get("aggregation") != "equal_plant_arithmetic_mean":
        raise ValueError("records must specify equal plant weights")
    if payload.get("reference_kind") != "published_reconstruction_reference":
        raise ValueError("records must identify the reconstruction reference")
    records = payload["records"]
    if not isinstance(records, list):
        raise ValueError("records must be an array")
    expected = {(model, plant) for model in METHODS for plant in plants}
    indexed = {}
    for record in records:
        key = (record["model"], record["plant_id"])
        if key not in expected:
            raise ValueError(f"unexpected method/plant pair: {key}")
        if key in indexed:
            raise ValueError(f"duplicate method/plant pair: {key}")
        source = record["source"]
        if (not isinstance(source.get("sha256"), str)
                or not re.fullmatch(r"[0-9a-f]{64}", source["sha256"])):
            raise ValueError(f"{key}: invalid source SHA256")
        for group, metrics in GROUPS.items():
            if not isinstance(record[group], dict) or set(record[group]) != set(metrics):
                raise ValueError(f"{key}/{group}: missing or unexpected metric fields")
            for metric in metrics:
                _number(record[group][metric], f"{key}/{group}/{metric}",
                        fraction=metric == "f_score_5mm")
        indexed[key] = record
    missing = expected - indexed.keys()
    if missing:
        raise ValueError(f"missing {len(missing)} method/plant pair(s): {sorted(missing)}")

    models = {}
    for model, display_name in METHODS.items():
        models[model] = {"display_name": display_name, "n_plants": len(plants)}
        for group, metrics in GROUPS.items():
            models[model][group] = {
                metric: math.fsum(indexed[(model, p)][group][metric] for p in plants) / len(plants)
                for metric in metrics
            }
    return {
        "schema_version": "tomatovggt-main-results-v1",
        "dataset": "TomatoWUR",
        "split": "test",
        "n_plants": len(plants),
        "plant_ids": plants,
        "aggregation": "equal_plant_arithmetic_mean",
        "reference_kind": payload["reference_kind"],
        "protocol": payload["protocol"],
        "historical_exposure": exposure,
        "checkpoint_selection": payload["checkpoint_selection"],
        "units": {"distance": "millimetre", "f_score_5mm": "fraction_0_to_1", "abs_rel": "unitless"},
        "inputs": {"per_plant_sha256": _sha256(records_path), "split_sha256": _sha256(split_path)},
        "models": models,
    }


def render_markdown(summary: dict) -> str:
    models = summary["models"]
    best = {
        (group, metric): (max if metric == "f_score_5mm" else min)(
            models[model][group][metric] for model in METHODS)
        for group, metric, *_ in COLUMNS
    }
    lines = [
        "# TomatoVGGT main results",
        "",
        "Ten TomatoWUR plants; equal arithmetic mean across plants. Best values are bold.",
        "",
        "| Method | " + " | ".join(column[2] for column in COLUMNS) + " |",
        "|---|" + "---:|" * len(COLUMNS),
    ]
    for model, display_name in METHODS.items():
        cells = [display_name]
        for group, metric, _, decimals, factor in COLUMNS:
            value = models[model][group][metric]
            cell = f"{value * factor:.{decimals}f}"
            if value == best[(group, metric)]:
                cell = f"**{cell}**"
            cells.append(cell)
        lines.append("| " + " | ".join(cells) + " |")
    selection = summary["checkpoint_selection"]
    lines += [
        "",
        "Distances use the published reconstruction reference, reference camera intrinsics and poses, "
        "and one median depth scale per plant across all views; no ICP or Sim(3) is applied. "
        "These metrics do not evaluate independently estimated cameras or native absolute scale.",
        "",
        "CD = (Accuracy + Completeness) / 2. F-score uses a 5 mm threshold. "
        "AbsRel is calculated after scale alignment over valid overlapping plant pixels. "
        "JSON retains unrounded values and stores F-scores as fractions; this table displays percentages.",
        "",
        f"TomatoVGGT uses update {selection['selected_update']}, selected by the lowest whole-plant "
        "validation CD on six validation plants (earlier update breaks ties), with all 15 views per test plant. "
        "The five baseline results retain their recorded input resolutions and valid-point support.",
        "",
        "This is a retrospective test split with historical development exposure. "
        + summary["historical_exposure"],
        "",
    ]
    return "\n".join(lines)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--records", type=Path, default=ROOT / "results/metrics/per_plant.json")
    parser.add_argument("--split", type=Path, default=ROOT / "datasets/splits/main_benchmark.json")
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args(argv)
    try:
        summary = summarize(args.records, args.split)
        markdown = render_markdown(summary)
        if args.output_dir is None:
            print(markdown, end="")
        else:
            targets = (args.output_dir / "main_results.json", args.output_dir / "main_results.md")
            inputs = {args.records.resolve(), args.split.resolve()}
            if any(target.resolve() in inputs for target in targets):
                raise ValueError("output files must not overwrite input records or split")
            args.output_dir.mkdir(parents=True, exist_ok=True)
            targets[0].write_text(json.dumps(summary, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
            targets[1].write_text(markdown, encoding="utf-8")
    except (OSError, ValueError, KeyError, TypeError) as error:
        parser.exit(2, f"error: {error}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())

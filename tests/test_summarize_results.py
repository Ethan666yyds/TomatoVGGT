"""Behavior checks for the paper cohort and the retained domain summaries."""
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("summary", ROOT / "scripts/summarize_results.py")
summary = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(summary)
SPLIT = ROOT / "datasets/splits/main_benchmark.json"
RECORDS = ROOT / "results/metrics"

# Published Table 2 display values, transcribed independently of the summarizer.
PAPER_ROWS = [
    "24.463 45.309 3.617 20.93 36.046 68.228 3.865 18.59 0.09035",
    "23.549 43.268 3.830 22.22 33.410 63.307 3.513 21.93 0.09029",
    "41.495 79.654 3.336 19.05 80.846 158.326 3.366 15.17 0.13139",
    "47.883 82.753 13.014 9.79 61.908 107.280 16.535 5.88 0.15284",
    "93.350 180.680 6.020 8.23 98.857 190.403 7.310 5.75 0.25013",
    "5.204 8.842 1.566 61.62 5.915 10.306 1.525 59.17 0.02185",
]


class SummaryTests(unittest.TestCase):
    def test_all_paper_cells_and_selection_exclusion(self):
        result = summary.summarize_combined(RECORDS, SPLIT)
        self.assertEqual(result["n_plants"], 32)
        self.assertEqual(result["domain_counts"], {"tomatowur": 10, "tomato_synth_validation": 22})
        selection = set(json.loads(SPLIT.read_text())["real"]["val"])
        for domain in result["domains"].values():
            self.assertFalse(selection & set(domain["plant_ids"]))
        for model, expected in zip(summary.METHODS, PAPER_ROWS):
            displayed = [
                f'{result["models"][model][group][metric] * factor:.{decimals}f}'
                for group, metric, _, decimals, factor in summary.COLUMNS
            ]
            self.assertEqual(displayed, expected.split())
        text = summary.render_markdown(result)
        self.assertIn("real reconstruction references and synthetic ground truth", text)
        self.assertIn("1/32", text)

    def test_domains_are_unchanged(self):
        for domain in ("tomatowur", "tomato_synth_validation"):
            result = summary.summarize(RECORDS / domain / "per_plant.json", SPLIT, domain)
            stored = ROOT / "results/tables" / domain
            self.assertEqual(result, json.loads((stored / "main_results.json").read_text()))
            self.assertEqual(summary.render_markdown(result), (stored / "main_results.md").read_text())

    def test_weight_is_per_plant_not_per_domain(self):
        with tempfile.TemporaryDirectory() as folder:
            records = Path(folder) / "metrics"
            shutil.copytree(RECORDS, records)
            for domain, value in (("tomatowur", 0), ("tomato_synth_validation", 32)):
                path = records / domain / "per_plant.json"
                data = json.loads(path.read_text())
                for row in data["records"]:
                    row["whole_plant"]["chamfer_mm"] = value
                path.write_text(json.dumps(data))
            result = summary.summarize_combined(records, SPLIT)
            for model in result["models"].values():
                self.assertEqual(model["whole_plant"]["chamfer_mm"], 22)

    def test_incomplete_domain_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            records = Path(folder) / "metrics"
            shutil.copytree(RECORDS, records)
            path = records / "tomato_synth_validation/per_plant.json"
            data = json.loads(path.read_text())
            data["records"].pop()
            path.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError, "missing 1 method/plant"):
                summary.summarize_combined(records, SPLIT)

    def test_checkpoint_selection_plant_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            split = Path(folder) / "split.json"
            data = json.loads(SPLIT.read_text())
            data["real"]["test"][0] = data["real"]["val"][0]
            split.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError, "overlap training or validation"):
                summary.summarize_combined(RECORDS, split)

    def test_cli_export_and_custom_paths(self):
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / "out"
            command = [sys.executable, str(ROOT / "scripts/summarize_results.py"),
                       "--dataset", "tomato3d", "--records-root", str(RECORDS), "--split", str(SPLIT)]
            printed = subprocess.run(command, capture_output=True, text=True, check=True).stdout
            subprocess.run(command + ["--output-dir", str(output)], capture_output=True, check=True)
            self.assertEqual(printed, (output / "main_results.md").read_text())
            self.assertEqual(json.loads((output / "main_results.json").read_text())["n_plants"], 32)
            invalid = subprocess.run(command + ["--records", str(RECORDS / "tomatowur/per_plant.json")], capture_output=True)
            self.assertEqual(invalid.returncode, 2)


if __name__ == "__main__":
    unittest.main()

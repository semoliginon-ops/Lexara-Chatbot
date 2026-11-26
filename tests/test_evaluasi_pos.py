"""Regression tests for development-only POS evaluation."""
import unittest

from tools.evaluasi_pos import _score, evaluate_records, load_development_records


class PosEvaluationTests(unittest.TestCase):
    def test_score_counts_abstention_as_not_correct(self):
        result = _score(["NOUN", "VERB", "ADJ"], ["NOUN", None, "NOUN"])
        self.assertEqual(result["total"], 3)
        self.assertEqual(result["predicted"], 2)
        self.assertEqual(result["correct"], 1)
        self.assertAlmostEqual(result["coverage"], 2 / 3)
        self.assertAlmostEqual(result["accuracy"], 1 / 3)
        self.assertAlmostEqual(result["selective_accuracy"], 1 / 2)
        self.assertEqual(result["confusion"]["VERB"]["NO_PREDICTION"], 1)

    def test_empty_score_returns_zero_metrics(self):
        result = _score([], [])
        self.assertEqual(result["total"], 0)
        self.assertEqual(result["coverage"], 0.0)
        self.assertEqual(result["accuracy"], 0.0)
        self.assertEqual(result["selective_accuracy"], 0.0)

    def test_rejects_test_records(self):
        with self.assertRaisesRegex(ValueError, "development"):
            evaluate_records([{"split": "test"}], {})

    def test_loads_only_development_records(self):
        import json
        import tempfile
        from pathlib import Path

        rows = [
            {"id": "pos_0001", "split": "development"},
            {"id": "pos_0002", "split": "test"},
        ]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "dataset.jsonl"
            path.write_text("\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8")
            result = load_development_records(path)
        self.assertEqual([item["id"] for item in result], ["pos_0001"])


if __name__ == "__main__":
    unittest.main()

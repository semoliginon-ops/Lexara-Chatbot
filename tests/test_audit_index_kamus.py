"""Tests for streaming dictionary-index audit."""
import json
import tempfile
import unittest
from pathlib import Path

from tools.audit_index_kamus import audit_index


SHARDS = ("a-c", "d-f", "g-i", "j-l", "m-o", "p-r", "s-u", "v-z")


class DictionaryIndexAuditTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.data_dir = self.root / "data" / "kamus"
        self.index_dir = self.data_dir / "index"
        self.data_dir.mkdir(parents=True)
        self.index_dir.mkdir()

        entry = {
            "id": "K0001",
            "lemma": "makan",
            "pos": ["VERB"],
            "senses": [{"sense_id": "K0001-S1", "definition": "Memasukkan makanan."}],
            "register": ["neutral"],
            "variants": [],
            "derived_forms": ["makanan", "memakan"],
        }
        (self.data_dir / "batch-001.jsonl").write_text(
            json.dumps(entry, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        for shard in SHARDS:
            (self.index_dir / f"{shard}.tsv").write_text(
                f"# Token index — {shard}\n"
                "# token\\tid\\tlemma\\ttype\\tbatch\n",
                encoding="utf-8",
            )

    def tearDown(self):
        self.temp.cleanup()

    def write_rows(self, rows_by_shard):
        for shard in SHARDS:
            rows = rows_by_shard.get(shard, [])
            path = self.index_dir / f"{shard}.tsv"
            path.write_text(
                f"# Token index — {shard}\n"
                "# token\\tid\\tlemma\\ttype\\tbatch\n"
                + "".join("\t".join(row) + "\n" for row in rows),
                encoding="utf-8",
            )

    def valid_rows(self):
        return {
            "m-o": [
                ("makan", "K0001", "makan", "lemma", "batch-001"),
                ("makanan", "K0001", "makan", "derived_form", "batch-001"),
                ("memakan", "K0001", "makan", "derived_form", "batch-001"),
            ]
        }

    def audit(self):
        return audit_index(
            self.data_dir,
            self.index_dir,
            expected_batches=1,
            expected_entries=1,
        )

    def test_accepts_index_matching_batch_source(self):
        self.write_rows(self.valid_rows())
        report = self.audit()
        self.assertTrue(report["ok"], report)
        self.assertEqual(report["expected_rows"], 3)
        self.assertEqual(report["actual_rows"], 3)
        self.assertEqual(len(report["omitted_optional_rows"]), 0)

    def test_allows_unindexed_optional_derived_form(self):
        rows = self.valid_rows()
        rows["m-o"] = rows["m-o"][:-1]
        self.write_rows(rows)
        report = self.audit()
        self.assertTrue(report["ok"], report)
        self.assertEqual(len(report["missing_lemma_rows"]), 0)
        self.assertEqual(len(report["omitted_optional_rows"]), 1)

    def test_reports_missing_lemma_index_row(self):
        self.write_rows({})
        report = self.audit()
        self.assertFalse(report["ok"])
        self.assertEqual(len(report["missing_lemma_rows"]), 1)
        self.assertEqual(report["missing_lemma_rows"][0][0][0], "makan")

    def test_reports_extra_index_row(self):
        rows = self.valid_rows()
        rows["m-o"].append(
            ("minum", "K0002", "minum", "lemma", "batch-001")
        )
        self.write_rows(rows)
        report = self.audit()
        self.assertFalse(report["ok"])
        self.assertEqual(len(report["extra_rows"]), 1)

    def test_reports_token_in_wrong_shard(self):
        rows = self.valid_rows()
        rows["m-o"] = rows["m-o"][1:]
        rows["a-c"] = [
            ("makan", "K0001", "makan", "lemma", "batch-001")
        ]
        self.write_rows(rows)
        report = self.audit()
        self.assertFalse(report["ok"])
        self.assertTrue(any("salah shard" in error for error in report["errors"]))


if __name__ == "__main__":
    unittest.main()

"""Tests for POS dataset validator."""
import json
import tempfile
import unittest
from pathlib import Path

from tools.validasi_dataset_pos import (
    PosDatasetFormatError,
    validate_pos_dataset,
)


def record():
    return {
        "id": "pos_0001",
        "split": "development",
        "text": "Aku makan.",
        "tokens": [
            {"token": "aku", "gold_pos": "PRON", "gold_status": "resolved"},
            {"token": "makan", "gold_pos": "VERB", "gold_status": "resolved"},
            {"token": ".", "gold_pos": None, "gold_status": "not_applicable"},
        ],
        "phenomena": ["kalimat_sederhana"],
        "notes": "",
    }


class PosDatasetValidatorTests(unittest.TestCase):
    def validate_records(self, records):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "dataset.jsonl"
            path.write_text(
                "".join(json.dumps(item, ensure_ascii=False) + "\n" for item in records),
                encoding="utf-8",
            )
            return validate_pos_dataset(path)

    def test_valid_record_returns_counts(self):
        result = self.validate_records([record()])
        self.assertEqual(result, {
            "sentences": 1, "tokens": 3, "development": 1, "test": 0
        })

    def test_valid_ambiguous_token_is_allowed(self):
        item = record()
        item["text"] = "Jalan."
        item["tokens"] = [
            {"token": "jalan", "gold_pos": None, "gold_status": "ambiguous"},
            {"token": ".", "gold_pos": None, "gold_status": "not_applicable"},
        ]
        self.assertEqual(self.validate_records([item])["tokens"], 2)

    def test_duplicate_id_is_rejected(self):
        item = record()
        with self.assertRaisesRegex(PosDatasetFormatError, "duplikat"):
            self.validate_records([item, dict(item)])

    def test_tokenizer_mismatch_is_rejected(self):
        item = record()
        item["tokens"][0]["token"] = "Aku"
        with self.assertRaisesRegex(PosDatasetFormatError, "token tidak cocok"):
            self.validate_records([item])

    def test_unknown_pos_label_is_rejected(self):
        item = record()
        item["tokens"][0]["gold_pos"] = "AUX"
        with self.assertRaisesRegex(PosDatasetFormatError, "label POS tidak resmi"):
            self.validate_records([item])

    def test_resolved_without_label_is_rejected(self):
        item = record()
        item["tokens"][0]["gold_pos"] = None
        with self.assertRaisesRegex(PosDatasetFormatError, "resolved harus memiliki"):
            self.validate_records([item])

    def test_unknown_with_label_is_rejected(self):
        item = record()
        item["tokens"][0]["gold_status"] = "unknown"
        with self.assertRaisesRegex(PosDatasetFormatError, "harus memiliki gold_pos null"):
            self.validate_records([item])

    def test_invalid_split_is_rejected(self):
        item = record()
        item["split"] = "validation"
        with self.assertRaisesRegex(PosDatasetFormatError, "split harus"):
            self.validate_records([item])

    def test_empty_dataset_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "empty.jsonl"
            path.write_text("", encoding="utf-8")
            with self.assertRaisesRegex(PosDatasetFormatError, "tidak memiliki record"):
                validate_pos_dataset(path)


if __name__ == "__main__":
    unittest.main()

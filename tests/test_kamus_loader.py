"""Regression tests for tools.kamus_loader."""
import json
import tempfile
import unittest
from pathlib import Path

from tools.kamus_loader import (
    DictionaryFormatError,
    load_batch,
    load_dictionary,
    load_dictionary_directory,
)


def entry(entry_id="K0001", lemma="makan"):
    return {
        "id": entry_id,
        "lemma": lemma,
        "pos": ["VERB"],
        "senses": [
            {"sense_id": f"{entry_id}-S1", "definition": "Memasukkan makanan."}
        ],
        "register": ["neutral"],
        "variants": [],
        "derived_forms": ["memakan"],
        "synonyms": [],
        "antonyms": [],
        "related_terms": [],
        "usage_notes": [],
    }


class DictionaryLoaderTests(unittest.TestCase):
    def write_jsonl(self, directory, filename, records):
        path = Path(directory) / filename
        path.write_text(
            "".join(json.dumps(record, ensure_ascii=False) + "\n" for record in records),
            encoding="utf-8",
        )
        return path

    def test_loads_single_jsonl_batch(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write_jsonl(tmp, "batch-001.jsonl", [entry()])
            loaded = load_batch(path)
            self.assertEqual(len(loaded), 1)
            self.assertEqual(loaded[0]["lemma"], "makan")

    def test_preserves_all_original_fields_and_values(self):
        original = entry()
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write_jsonl(tmp, "batch-001.jsonl", [original])
            loaded = load_batch(path)
            self.assertEqual(loaded[0], original)

    def test_loads_multiple_batches(self):
        with tempfile.TemporaryDirectory() as tmp:
            first = self.write_jsonl(tmp, "batch-001.jsonl", [entry("K0001", "aku")])
            second = self.write_jsonl(tmp, "batch-002.jsonl", [entry("K0002", "saya")])
            loaded = load_dictionary([first, second])
            self.assertEqual([item["id"] for item in loaded], ["K0001", "K0002"])

    def test_directory_loader_uses_batch_filename_order(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.write_jsonl(tmp, "batch-002.jsonl", [entry("K0002", "saya")])
            self.write_jsonl(tmp, "batch-001.jsonl", [entry("K0001", "aku")])
            loaded = load_dictionary_directory(tmp)
            self.assertEqual([item["id"] for item in loaded], ["K0001", "K0002"])

    def test_rejects_invalid_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "batch-001.jsonl"
            path.write_text("{not-json}\n", encoding="utf-8")
            with self.assertRaisesRegex(DictionaryFormatError, "JSON tidak valid"):
                load_batch(path)

    def test_rejects_non_object_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "batch-001.jsonl"
            path.write_text('["not", "an", "object"]\n', encoding="utf-8")
            with self.assertRaisesRegex(DictionaryFormatError, "objek JSON"):
                load_batch(path)

    def test_rejects_missing_required_field(self):
        record = entry()
        del record["lemma"]
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write_jsonl(tmp, "batch-001.jsonl", [record])
            with self.assertRaisesRegex(DictionaryFormatError, "field wajib hilang"):
                load_batch(path)

    def test_rejects_invalid_id_format(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write_jsonl(tmp, "batch-001.jsonl", [entry("BAD-ID")])
            with self.assertRaisesRegex(DictionaryFormatError, "K0001"):
                load_batch(path)

    def test_rejects_empty_required_array(self):
        record = entry()
        record["pos"] = []
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write_jsonl(tmp, "batch-001.jsonl", [record])
            with self.assertRaisesRegex(DictionaryFormatError, "pos harus"):
                load_batch(path)

    def test_rejects_duplicate_ids_across_batches(self):
        with tempfile.TemporaryDirectory() as tmp:
            first = self.write_jsonl(tmp, "batch-001.jsonl", [entry("K0001", "makan")])
            second = self.write_jsonl(tmp, "batch-002.jsonl", [entry("K0001", "minum")])
            with self.assertRaisesRegex(DictionaryFormatError, "ID duplikat"):
                load_dictionary([first, second])

    def test_rejects_duplicate_lemmas_case_insensitively(self):
        with tempfile.TemporaryDirectory() as tmp:
            first = self.write_jsonl(tmp, "batch-001.jsonl", [entry("K0001", "Makan")])
            second = self.write_jsonl(tmp, "batch-002.jsonl", [entry("K0002", "makan")])
            with self.assertRaisesRegex(DictionaryFormatError, "lemma duplikat"):
                load_dictionary([first, second])

    def test_rejects_empty_file_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(DictionaryFormatError, "Tidak ditemukan"):
                load_dictionary_directory(tmp)


if __name__ == "__main__":
    unittest.main()

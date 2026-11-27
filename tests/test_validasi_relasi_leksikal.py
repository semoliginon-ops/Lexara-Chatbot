"""Regression tests for sense-scoped lexical relation validation."""
import unittest
from pathlib import Path
from unittest.mock import patch

from tools.validasi_relasi_leksikal import (
    validate_entries_relations,
    validate_entry_relations,
    validate_relation_batches,
)


def legacy_entry():
    return {
        "id": "K0001",
        "lemma": "makan",
        "pos": ["VERB"],
        "senses": [
            {"sense_id": "K0001-S1", "definition": "Memasukkan makanan."}
        ],
        "register": ["neutral"],
        "synonyms": ["menyantap"],
        "antonyms": [],
        "related_terms": ["makanan"],
    }


class LexicalRelationValidationTests(unittest.TestCase):
    def test_accepts_legacy_entry_without_sense_relations(self):
        self.assertEqual(validate_entry_relations(legacy_entry()), [])

    def test_accepts_optional_sense_scoped_relations(self):
        entry = legacy_entry()
        entry["senses"][0]["synonyms"] = ["menyantap"]
        entry["senses"][0]["antonyms"] = []
        entry["senses"][0]["related_terms"] = ["makanan"]
        self.assertEqual(validate_entry_relations(entry), [])

    def test_accepts_omitted_relation_fields(self):
        entry = {
            "lemma": "rumah",
            "senses": [{"sense_id": "S1", "definition": "Bangunan tempat tinggal."}],
        }
        self.assertEqual(validate_entry_relations(entry), [])

    def test_rejects_non_array_relation_field(self):
        entry = legacy_entry()
        entry["synonyms"] = "santap"
        errors = validate_entry_relations(entry)
        self.assertTrue(any("synonyms harus berupa array" in error for error in errors))

    def test_rejects_non_string_or_blank_relation_items(self):
        entry = legacy_entry()
        entry["synonyms"] = ["", 12]
        errors = validate_entry_relations(entry)
        self.assertEqual(len(errors), 2)
        self.assertTrue(all("teks nonkosong" in error for error in errors))

    def test_rejects_duplicate_after_unicode_casefold_normalization(self):
        entry = legacy_entry()
        entry["synonyms"] = ["SANTAP", "santap"]
        errors = validate_entry_relations(entry)
        self.assertTrue(any("duplikat setelah normalisasi" in error for error in errors))

    def test_rejects_relation_to_own_lemma(self):
        entry = legacy_entry()
        entry["related_terms"] = ["Makan"]
        errors = validate_entry_relations(entry)
        self.assertTrue(any("lemma sendiri" in error for error in errors))

    def test_rejects_sense_relation_without_sense_id(self):
        entry = legacy_entry()
        entry["senses"][0]["synonyms"] = ["menyantap"]
        del entry["senses"][0]["sense_id"]
        errors = validate_entry_relations(entry)
        self.assertTrue(any("sense_id wajib" in error for error in errors))

    def test_does_not_require_sense_id_when_no_sense_relations(self):
        entry = legacy_entry()
        del entry["senses"][0]["sense_id"]
        self.assertEqual(validate_entry_relations(entry), [])

    def test_rejects_non_object_sense_when_relations_are_checked(self):
        entry = legacy_entry()
        entry["senses"].append("not-an-object")
        errors = validate_entry_relations(entry)
        self.assertTrue(any("sense harus berupa objek" in error for error in errors))

    def test_multiple_batches_are_processed_one_by_one(self):
        fake_results = [(2, []), (3, ["K0003: relasi duplikat"])]
        with patch("tools.validasi_relasi_leksikal.validate_relation_batch", side_effect=fake_results) as mocked:
            results = validate_relation_batches([Path("a.jsonl"), Path("b.jsonl")])
        self.assertEqual(results, [
            (Path("a.jsonl"), 2, []),
            (Path("b.jsonl"), 3, ["K0003: relasi duplikat"]),
        ])
        self.assertEqual(mocked.call_count, 2)

    def test_validates_all_entries_and_reports_entry_ids(self):
        good = legacy_entry()
        bad = legacy_entry()
        bad["id"] = "K0002"
        bad["synonyms"] = ["makan"]
        errors = validate_entries_relations([good, bad])
        self.assertEqual(len(errors), 1)
        self.assertIn("K0002", errors[0])


if __name__ == "__main__":
    unittest.main()

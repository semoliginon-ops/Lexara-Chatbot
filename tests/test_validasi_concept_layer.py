"""Tests terfokus untuk validator Concept Layer v1 dengan fixture sintetis."""
import json
import tempfile
import unittest
from pathlib import Path

from tools.validasi_concept_layer import (
    load_sense_ids,
    validate_concept_layer,
    validate_records,
)

FIXTURES = Path(__file__).parent / "fixtures" / "concept_layer"


class ConceptLayerValidationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.concepts = self.root / "concepts.jsonl"
        self.mappings = self.root / "sense_concept_map.jsonl"
        self.relations = self.root / "concept_relations.jsonl"
        self.sense_index = FIXTURES / "sense_index.jsonl"
        self._write_fixture_files()

    def tearDown(self):
        self.tmp.cleanup()

    def _write_fixture_files(self):
        for name, target in (
            ("concepts.valid.jsonl", self.concepts),
            ("sense_concept_map.valid.jsonl", self.mappings),
            ("concept_relations.valid.jsonl", self.relations),
        ):
            target.write_text((FIXTURES / name).read_text(encoding="utf-8"), encoding="utf-8")

    def _read_records(self, path):
        return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]

    def _write_records(self, path, records):
        path.write_text("".join(json.dumps(item, ensure_ascii=False) + "\n" for item in records), encoding="utf-8")

    def _validate(self):
        return validate_concept_layer(self.concepts, self.mappings, self.relations, [self.sense_index])

    def test_accepts_valid_synthetic_fixture(self):
        counts, errors = self._validate()
        self.assertEqual(errors, [])
        self.assertEqual(counts, {"concepts": 2, "mappings": 1, "relations": 1, "sense_ids": 1})

    def test_allows_empty_concept_layer_files(self):
        for path in (self.concepts, self.mappings, self.relations):
            path.write_text("", encoding="utf-8")
        _, errors = self._validate()
        self.assertEqual(errors, [])

    def test_rejects_invalid_json_line(self):
        self.concepts.write_text("{broken}\n", encoding="utf-8")
        _, errors = self._validate()
        self.assertTrue(any("JSON tidak valid" in error for error in errors))

    def test_rejects_non_object_json_line(self):
        self.concepts.write_text("[]\n", encoding="utf-8")
        _, errors = self._validate()
        self.assertTrue(any("objek JSON" in error for error in errors))

    def test_rejects_unknown_and_missing_fields(self):
        records = self._read_records(self.concepts)
        records[0]["unexpected"] = True
        del records[0]["label"]
        self._write_records(self.concepts, records)
        _, errors = self._validate()
        self.assertTrue(any("field wajib hilang" in error for error in errors))
        self.assertTrue(any("field tidak dikenal" in error for error in errors))

    def test_rejects_bad_concept_id_format(self):
        records = self._read_records(self.concepts)
        records[0]["concept_id"] = "C12"
        self._write_records(self.concepts, records)
        _, errors = self._validate()
        self.assertTrue(any("minimal enam digit" in error for error in errors))

    def test_rejects_duplicate_concept_id(self):
        records = self._read_records(self.concepts)
        records[1]["concept_id"] = records[0]["concept_id"]
        self._write_records(self.concepts, records)
        _, errors = self._validate()
        self.assertTrue(any("concept_id: duplikat" in error for error in errors))

    def test_rejects_blank_label_and_definition(self):
        records = self._read_records(self.concepts)
        records[0]["label"] = " "
        records[0]["definition"] = ""
        self._write_records(self.concepts, records)
        _, errors = self._validate()
        self.assertTrue(any(".label" in error for error in errors))
        self.assertTrue(any(".definition" in error for error in errors))

    def test_rejects_unknown_status(self):
        records = self._read_records(self.concepts)
        records[0]["status"] = "active"
        self._write_records(self.concepts, records)
        _, errors = self._validate()
        self.assertTrue(any(".status" in error for error in errors))

    def test_rejects_malformed_evidence(self):
        records = self._read_records(self.concepts)
        records[0]["evidence"]["source_ref"] = 17
        self._write_records(self.concepts, records)
        _, errors = self._validate()
        self.assertTrue(any("source_ref" in error for error in errors))

    def test_rejects_unresolved_sense_and_concept_references(self):
        records = self._read_records(self.mappings)
        records[0]["sense_id"] = "K9999-S1"
        records[0]["concept_id"] = "C999999"
        self._write_records(self.mappings, records)
        _, errors = self._validate()
        self.assertTrue(any("tidak ditemukan pada --sense-index" in error for error in errors))
        self.assertTrue(any("konsep tidak ditemukan" in error for error in errors))

    def test_rejects_duplicate_mapping_pair(self):
        records = self._read_records(self.mappings)
        records.append(dict(records[0]))
        self._write_records(self.mappings, records)
        _, errors = self._validate()
        self.assertTrue(any("pasangan sense_id + concept_id duplikat" in error for error in errors))

    def test_rejects_bad_relation_type_and_self_reference(self):
        records = self._read_records(self.relations)
        records[0]["type"] = "NEAR_TO"
        records[0]["target"] = records[0]["source"]
        self._write_records(self.relations, records)
        _, errors = self._validate()
        self.assertTrue(any("tipe relasi tidak dikenal" in error for error in errors))
        self.assertTrue(any("relasi diri sendiri" in error for error in errors))

    def test_rejects_duplicate_relation_id_and_triple(self):
        records = self._read_records(self.relations)
        duplicate = dict(records[0])
        records.append(duplicate)
        self._write_records(self.relations, records)
        _, errors = self._validate()
        self.assertTrue(any("relation_id: duplikat" in error for error in errors))
        self.assertTrue(any("kombinasi source + type + target duplikat" in error for error in errors))

    def test_rejects_unresolved_relation_endpoints(self):
        records = self._read_records(self.relations)
        records[0]["target"] = "C999999"
        self._write_records(self.relations, records)
        _, errors = self._validate()
        self.assertTrue(any("konsep tidak ditemukan" in error for error in errors))

    def test_sense_index_is_read_only_and_resolves_nested_senses(self):
        original = self.sense_index.read_text(encoding="utf-8")
        sense_ids, errors = load_sense_ids([self.sense_index])
        self.assertEqual(errors, [])
        self.assertEqual(sense_ids, {"K0020-S1"})
        self.assertEqual(self.sense_index.read_text(encoding="utf-8"), original)

    def test_requires_sense_index(self):
        _, errors = validate_concept_layer(self.concepts, self.mappings, self.relations, [])
        self.assertTrue(any("--sense-index wajib" in error for error in errors))


if __name__ == "__main__":
    unittest.main()

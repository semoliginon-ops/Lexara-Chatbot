"""Tes terfokus untuk pembaca Concept Layer v1."""
import json
import tempfile
import unittest
from pathlib import Path
from tools.concept_layer_loader import ConceptLayerLoadError, load_concept_layer

FIXTURES = Path(__file__).parent / "fixtures" / "concept_layer"

class ConceptLayerLoaderTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.concepts, self.mappings, self.relations = (self.root / n for n in ("concepts.jsonl", "mappings.jsonl", "relations.jsonl"))
        for name, target in (("concepts.valid.jsonl", self.concepts), ("sense_concept_map.valid.jsonl", self.mappings), ("concept_relations.valid.jsonl", self.relations)):
            target.write_text((FIXTURES / name).read_text(encoding="utf-8"), encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def _records(self, path):
        return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]

    def _write(self, path, records):
        path.write_text("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in records), encoding="utf-8")

    def _load(self):
        return load_concept_layer(self.concepts, self.mappings, self.relations)

    def test_exposes_only_reviewed_records(self):
        data = self._load()
        self.assertEqual([x["concept_id"] for x in data["concepts"]], ["C000001"])
        self.assertEqual([x["sense_id"] for x in data["mappings"]], ["K0020-S1"])
        self.assertEqual(data["relations"], [])

    def test_mapping_hidden_if_target_concept_not_reviewed(self):
        rows = self._records(self.concepts); rows[0]["status"] = "proposed"; self._write(self.concepts, rows)
        data = self._load()
        self.assertEqual(data["concepts"], [])
        self.assertEqual(data["mappings"], [])

    def test_relation_hidden_if_either_endpoint_not_reviewed(self):
        rows = self._records(self.concepts); rows[0]["status"] = "proposed"; rows[1]["status"] = "reviewed"; self._write(self.concepts, rows)
        rows = self._records(self.relations); rows[0]["status"] = "reviewed"; self._write(self.relations, rows)
        self.assertEqual(self._load()["relations"], [])

    def test_relation_exposed_when_relation_and_both_endpoints_reviewed(self):
        rows = self._records(self.concepts); rows[1]["status"] = "reviewed"; self._write(self.concepts, rows)
        rows = self._records(self.relations); rows[0]["status"] = "reviewed"; self._write(self.relations, rows)
        self.assertEqual([x["relation_id"] for x in self._load()["relations"]], ["R000001"])

    def test_empty_files_are_valid_empty_layer(self):
        for path in (self.concepts, self.mappings, self.relations): path.write_text("", encoding="utf-8")
        self.assertEqual(self._load(), {"concepts": [], "mappings": [], "relations": []})

    def test_missing_file_raises_instead_of_looking_empty(self):
        self.relations.unlink()
        with self.assertRaises(ConceptLayerLoadError): self._load()

    def test_invalid_json_rejected(self):
        self.concepts.write_text("{bad json}\n", encoding="utf-8")
        with self.assertRaises(ConceptLayerLoadError): self._load()

    def test_unknown_mapping_concept_rejected(self):
        rows = self._records(self.mappings); rows[0]["concept_id"] = "C999999"; self._write(self.mappings, rows)
        with self.assertRaises(ConceptLayerLoadError): self._load()

    def test_unknown_relation_endpoint_rejected(self):
        rows = self._records(self.relations); rows[0]["target"] = "C999999"; self._write(self.relations, rows)
        with self.assertRaises(ConceptLayerLoadError): self._load()

    def test_invalid_status_rejected(self):
        rows = self._records(self.concepts); rows[0]["status"] = "active"; self._write(self.concepts, rows)
        with self.assertRaises(ConceptLayerLoadError): self._load()

    def test_duplicate_concept_id_rejected(self):
        rows = self._records(self.concepts); rows[1]["concept_id"] = rows[0]["concept_id"]; self._write(self.concepts, rows)
        with self.assertRaises(ConceptLayerLoadError): self._load()

    def test_source_files_remain_unchanged(self):
        before = [p.read_bytes() for p in (self.concepts, self.mappings, self.relations)]
        self._load()
        self.assertEqual([p.read_bytes() for p in (self.concepts, self.mappings, self.relations)], before)

if __name__ == "__main__":
    unittest.main()

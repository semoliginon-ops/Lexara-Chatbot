"""Tes terfokus untuk adapter kandidat sense ke Concept Layer."""
import unittest

from tools.concept_sense_adapter import (
    ConceptSenseAdapterError,
    map_sense_candidates_to_concepts,
)


def concept(concept_id="C000001", status="reviewed"):
    return {
        "concept_id": concept_id,
        "label": "kendaraan",
        "definition": "Alat transportasi.",
        "status": status,
        "evidence": {},
    }


def mapping(sense_id="K0001-S1", concept_id="C000001", status="reviewed"):
    return {
        "sense_id": sense_id,
        "concept_id": concept_id,
        "status": status,
        "evidence": {},
    }


def candidate(entry_id="K0001", senses=None, match_type="lemma"):
    entry = {
        "id": entry_id,
        "lemma": "kendaraan",
        "senses": senses if senses is not None else [
            {"sense_id": "K0001-S1", "definition": "Makna pertama."}
        ],
    }
    return {
        "entry_id": entry_id,
        "lemma": "kendaraan",
        "matched_form": "kendaraan",
        "match_type": match_type,
        "entry": entry,
    }


class ConceptSenseAdapterTests(unittest.TestCase):
    def setUp(self):
        self.layer = {
            "concepts": [concept()],
            "mappings": [mapping()],
            "relations": [],
        }

    def test_attaches_reviewed_concept_to_matching_sense(self):
        result = map_sense_candidates_to_concepts([candidate()], self.layer)
        self.assertEqual(result[0]["sense_id"], "K0001-S1")
        self.assertEqual(result[0]["concepts"][0]["concept_id"], "C000001")
        self.assertEqual(result[0]["mapping_status"], "mapped")

    def test_unmapped_sense_is_preserved(self):
        item = candidate(senses=[{"sense_id": "K0001-S2"}])
        result = map_sense_candidates_to_concepts([item], self.layer)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["concepts"], [])
        self.assertEqual(result[0]["mapping_status"], "unmapped")

    def test_multiple_reviewed_mappings_are_preserved(self):
        self.layer["concepts"].append(concept("C000002"))
        self.layer["mappings"].append(mapping(concept_id="C000002"))
        result = map_sense_candidates_to_concepts([candidate()], self.layer)
        self.assertEqual(
            [x["concept_id"] for x in result[0]["concepts"]],
            ["C000001", "C000002"],
        )

    def test_unreviewed_mapping_is_ignored(self):
        self.layer["mappings"][0]["status"] = "proposed"
        result = map_sense_candidates_to_concepts([candidate()], self.layer)
        self.assertEqual(result[0]["concepts"], [])
        self.assertEqual(result[0]["mapping_status"], "unmapped")

    def test_mapping_to_unreviewed_concept_is_ignored(self):
        self.layer["concepts"][0]["status"] = "proposed"
        result = map_sense_candidates_to_concepts([candidate()], self.layer)
        self.assertEqual(result[0]["concepts"], [])

    def test_ambiguous_sense_candidates_are_not_collapsed(self):
        items = [
            candidate("K0001"),
            candidate("K0002", [{"sense_id": "K0002-S1"}]),
        ]
        result = map_sense_candidates_to_concepts(items, self.layer)
        self.assertEqual(
            [x["sense_id"] for x in result],
            ["K0001-S1", "K0002-S1"],
        )

    def test_candidate_match_metadata_is_preserved(self):
        item = candidate(match_type="derived_form")
        result = map_sense_candidates_to_concepts([item], self.layer)
        self.assertEqual(result[0]["match_type"], "derived_form")
        self.assertEqual(result[0]["matched_form"], "kendaraan")
        self.assertEqual(result[0]["entry_id"], "K0001")

    def test_concept_relations_do_not_create_unstated_mappings(self):
        self.layer["concepts"].append(concept("C000002"))
        self.layer["relations"] = [{
            "relation_id": "R000001",
            "source": "C000001",
            "type": "IS_A",
            "target": "C000002",
            "status": "reviewed",
        }]
        result = map_sense_candidates_to_concepts(
            [candidate(senses=[{"sense_id": "K0001-S2"}])],
            self.layer,
        )
        self.assertEqual(result[0]["concepts"], [])

    def test_empty_candidates_return_empty_result(self):
        self.assertEqual(map_sense_candidates_to_concepts([], self.layer), [])

    def test_invalid_candidate_without_sense_id_is_rejected(self):
        item = candidate(senses=[{"definition": "Tanpa ID."}])
        with self.assertRaises(ConceptSenseAdapterError):
            map_sense_candidates_to_concepts([item], self.layer)


if __name__ == "__main__":
    unittest.main()

"""Exactly 12 focused tests for sense-level clarification planner v1.1."""
import unittest

from tools.clarification_planner import plan_clarification


def candidate_ref(token_index=0, candidate_index=0):
    return {
        "source_field": "lexical_candidates",
        "token_index": token_index,
        "candidate_index": candidate_index,
    }


def sense_ref(token_index=0, candidate_index=0, sense_index=0, sense_id="K0016-S1"):
    return {
        "source_field": "lexical_candidates",
        "token_index": token_index,
        "candidate_index": candidate_index,
        "sense_index": sense_index,
        "sense_id": sense_id,
    }


def make_report(dimension="lexical_sense", token_index=0, parent=None):
    parent = parent or candidate_ref(token_index=token_index)
    return {
        "schema_version": "1.0",
        "source": {"snapshot_status": "assembled", "parser_status": "parsed"},
        "ambiguity": {
            "status": "ambiguous",
            "items": [{
                "dimension": dimension,
                "token_index": token_index,
                "candidate_refs": [parent],
                "evidence_refs": [],
                "status": "ambiguous",
                "reason": "multiple_candidates_preserved",
            }],
        },
        "communicative_intent": {
            "status": "unresolved", "label": "unknown", "candidates": []
        },
    }


def make_snapshot():
    return {
        "status": "assembled",
        "parser_status": "parsed",
        "tokens": [{
            "token": "bangun",
            "kind": "word",
            "lexical_candidates": [{
                "entry_id": "K0016",
                "lemma": "bangun",
                "entry": {
                    "id": "K0016",
                    "lemma": "bangun",
                    "senses": [
                        {
                            "sense_id": "K0016-S1",
                            "definition": "Beralih dari keadaan tidur ke keadaan sadar.",
                        },
                        {
                            "sense_id": "K0016-S2",
                            "definition": "Berdiri atau menjadi tegak dari posisi duduk atau berbaring.",
                        },
                    ],
                },
            }],
        }],
    }


def sense_opportunity(
    parent=None,
    refs=None,
    index=0,
    material=True,
    distinguishable=True,
    priority=0,
):
    parent = parent or candidate_ref()
    refs = refs or [
        sense_ref(sense_index=0, sense_id="K0016-S1"),
        sense_ref(sense_index=1, sense_id="K0016-S2"),
    ]
    return {
        "ambiguity_item_index": index,
        "parent_candidate_ref": parent,
        "sense_refs": refs,
        "material_to_next_response": material,
        "user_can_distinguish": distinguishable,
        "priority": priority,
    }


class ClarificationPlannerV11Tests(unittest.TestCase):
    def test_asks_for_two_valid_senses_inside_one_entry(self):
        report = make_report()
        snapshot = make_snapshot()
        result = plan_clarification(
            report, [sense_opportunity()], snapshot=snapshot
        )
        self.assertEqual(result["schema_version"], "1.1")
        self.assertEqual(result["decision"], "ask")
        self.assertEqual(result["focus"]["parent_candidate_ref"], candidate_ref())
        self.assertEqual(len(result["focus"]["sense_refs"]), 2)

    def test_abstains_when_sense_snapshot_is_missing(self):
        result = plan_clarification(make_report(), [sense_opportunity()])
        self.assertEqual(result["decision"], "abstain")
        self.assertEqual(result["reason"], "invalid_or_untraceable_sense_reference")

    def test_rejects_parent_candidate_not_in_ambiguity_item(self):
        wrong_parent = candidate_ref(candidate_index=2)
        result = plan_clarification(
            make_report(), [sense_opportunity(parent=wrong_parent)],
            snapshot=make_snapshot(),
        )
        self.assertEqual(result["decision"], "abstain")

    def test_rejects_token_index_not_matching_ambiguity_item(self):
        refs = [
            sense_ref(token_index=1, sense_index=0, sense_id="K0016-S1"),
            sense_ref(token_index=1, sense_index=1, sense_id="K0016-S2"),
        ]
        result = plan_clarification(
            make_report(), [sense_opportunity(refs=refs)],
            snapshot=make_snapshot(),
        )
        self.assertEqual(result["decision"], "abstain")

    def test_rejects_candidate_index_not_matching_parent(self):
        refs = [
            sense_ref(candidate_index=1, sense_index=0, sense_id="K0016-S1"),
            sense_ref(candidate_index=1, sense_index=1, sense_id="K0016-S2"),
        ]
        result = plan_clarification(
            make_report(), [sense_opportunity(refs=refs)],
            snapshot=make_snapshot(),
        )
        self.assertEqual(result["decision"], "abstain")

    def test_rejects_sense_index_out_of_range(self):
        refs = [
            sense_ref(sense_index=0, sense_id="K0016-S1"),
            sense_ref(sense_index=9, sense_id="K0016-S2"),
        ]
        result = plan_clarification(
            make_report(), [sense_opportunity(refs=refs)],
            snapshot=make_snapshot(),
        )
        self.assertEqual(result["decision"], "abstain")

    def test_rejects_sense_id_that_does_not_match_source_index(self):
        refs = [
            sense_ref(sense_index=0, sense_id="K0016-S2"),
            sense_ref(sense_index=1, sense_id="K0016-S1"),
        ]
        result = plan_clarification(
            make_report(), [sense_opportunity(refs=refs)],
            snapshot=make_snapshot(),
        )
        self.assertEqual(result["decision"], "abstain")

    def test_rejects_sense_without_nonempty_definition(self):
        snapshot = make_snapshot()
        snapshot["tokens"][0]["lexical_candidates"][0]["entry"]["senses"][1]["definition"] = " "
        result = plan_clarification(
            make_report(), [sense_opportunity()], snapshot=snapshot
        )
        self.assertEqual(result["decision"], "abstain")

    def test_rejects_duplicate_sense_references(self):
        first = sense_ref(sense_index=0, sense_id="K0016-S1")
        result = plan_clarification(
            make_report(), [sense_opportunity(refs=[first, dict(first)])],
            snapshot=make_snapshot(),
        )
        self.assertEqual(result["decision"], "abstain")

    def test_rejects_sense_references_for_nonlexical_dimension(self):
        result = plan_clarification(
            make_report(dimension="pos"), [sense_opportunity()],
            snapshot=make_snapshot(),
        )
        self.assertEqual(result["decision"], "abstain")

    def test_preserves_valid_v1_candidate_reference_path(self):
        report = {
            "ambiguity": {
                "status": "ambiguous",
                "items": [{
                    "dimension": "pos",
                    "token_index": 0,
                    "candidate_refs": [
                        candidate_ref(candidate_index=0),
                        candidate_ref(candidate_index=1),
                    ],
                    "status": "ambiguous",
                }],
            },
        }
        opportunity = {
            "ambiguity_item_index": 0,
            "candidate_refs": [
                candidate_ref(candidate_index=0),
                candidate_ref(candidate_index=1),
            ],
            "material_to_next_response": True,
            "user_can_distinguish": True,
            "priority": 0,
        }
        result = plan_clarification(report, [opportunity])
        self.assertEqual(result["schema_version"], "1.0")
        self.assertEqual(result["decision"], "ask")
        self.assertIn("candidate_refs", result["focus"])

    def test_selects_highest_priority_sense_opportunity_and_one_focus(self):
        parent0 = candidate_ref(token_index=0)
        parent1 = candidate_ref(token_index=1)
        report = {
            "ambiguity": {
                "status": "ambiguous",
                "items": [
                    {
                        "dimension": "lexical_sense",
                        "token_index": 0,
                        "candidate_refs": [parent0],
                        "status": "ambiguous",
                    },
                    {
                        "dimension": "lexical_sense",
                        "token_index": 1,
                        "candidate_refs": [parent1],
                        "status": "ambiguous",
                    },
                ],
            },
        }
        snapshot = make_snapshot()
        snapshot["tokens"].append({
            "token": "bisa",
            "kind": "word",
            "lexical_candidates": [{
                "entry_id": "K0026",
                "lemma": "bisa",
                "entry": {
                    "id": "K0026",
                    "lemma": "bisa",
                    "senses": [
                        {"sense_id": "K0026-S1", "definition": "Mampu atau sanggup melakukan sesuatu."},
                        {"sense_id": "K0026-S2", "definition": "Zat beracun yang dapat membahayakan tubuh."},
                    ],
                },
            }],
        })
        refs1 = [
            sense_ref(token_index=1, sense_index=0, sense_id="K0026-S1"),
            sense_ref(token_index=1, sense_index=1, sense_id="K0026-S2"),
        ]
        result = plan_clarification(report, [
            sense_opportunity(parent=parent0, priority=4),
            sense_opportunity(parent=parent1, refs=refs1, index=1, priority=1),
        ], snapshot=snapshot)
        self.assertEqual(result["decision"], "ask")
        self.assertEqual(result["focus"]["ambiguity_item_index"], 1)
        self.assertEqual(len(result["focus"]["sense_refs"]), 2)


if __name__ == "__main__":
    unittest.main()

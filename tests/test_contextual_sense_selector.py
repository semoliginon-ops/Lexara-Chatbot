"""Exactly 12 focused unit tests for Contextual Sense Selector v1."""
import copy
import unittest

from tools.contextual_sense_selector import (
    ContextualSenseSelectorError,
    select_contextual_sense,
)


def candidate(sense_id, lemma="uji"):
    return {
        "sense_id": sense_id,
        "lemma": lemma,
        "sense": {"definition": f"Makna {sense_id}"},
        "concepts": [],
    }


def item(sense_id, polarity="supports", strength="strong", rule_id="CE000001"):
    return {
        "sense_id": sense_id,
        "concept_ids": [],
        "polarity": polarity,
        "strength": strength,
        "source": "kurasi-uji",
        "rule_id": rule_id,
        "rationale": "Evidence eksplisit untuk pengujian.",
        "matched_conditions": [],
        "token_spans": [],
    }


class ContextualSenseSelectorTests(unittest.TestCase):
    def test_single_candidate_without_strong_contradiction_is_not_needed(self):
        result = select_contextual_sense(
            [candidate("K0001-S1")],
            [item("K0001-S1", polarity="supports")],
        )
        self.assertEqual(result["status"], "not_needed")
        self.assertEqual(result["selected_sense_id"], None)
        self.assertEqual(result["reason"], "single_candidate_no_context_decision")

    def test_no_candidates_returns_unresolved(self):
        result = select_contextual_sense([], [])
        self.assertEqual(result["status"], "unresolved")
        self.assertEqual(result["reason"], "no_candidates")
        self.assertIsNone(result["selected_sense_id"])

    def test_supported_sense_selected_when_all_alternatives_are_strongly_contradicted(self):
        candidates = [
            candidate("K0001-S1"),
            candidate("K0001-S2"),
            candidate("K0001-S3"),
        ]
        evidence = [
            item("K0001-S1", "supports", rule_id="CE000001"),
            item("K0001-S2", "contradicts", rule_id="CE000002"),
            item("K0001-S3", "contradicts", rule_id="CE000003"),
        ]
        result = select_contextual_sense(candidates, evidence)
        self.assertEqual(result["status"], "selected")
        self.assertEqual(result["selected_sense_id"], "K0001-S1")
        self.assertEqual(
            [entry["state"] for entry in result["candidate_audit"]],
            ["viable", "excluded", "excluded"],
        )

    def test_support_without_strongly_excluding_alternative_remains_ambiguous(self):
        result = select_contextual_sense(
            [candidate("K0001-S1"), candidate("K0001-S2")],
            [item("K0001-S1", "supports")],
        )
        self.assertEqual(result["status"], "ambiguous")
        self.assertEqual(result["reason"], "multiple_viable_senses")
        self.assertIsNone(result["selected_sense_id"])

    def test_two_senses_with_strong_support_remain_ambiguous(self):
        result = select_contextual_sense(
            [candidate("K0001-S1"), candidate("K0001-S2")],
            [
                item("K0001-S1", "supports", rule_id="CE000001"),
                item("K0001-S2", "supports", rule_id="CE000002"),
            ],
        )
        self.assertEqual(result["status"], "ambiguous")
        self.assertEqual(
            [entry["state"] for entry in result["candidate_audit"]],
            ["viable", "viable"],
        )

    def test_strong_support_and_contradiction_on_same_sense_is_conflicted(self):
        result = select_contextual_sense(
            [candidate("K0001-S1"), candidate("K0001-S2")],
            [
                item("K0001-S1", "supports", rule_id="CE000001"),
                item("K0001-S1", "contradicts", rule_id="CE000002"),
                item("K0001-S2", "contradicts", rule_id="CE000003"),
            ],
        )
        self.assertEqual(result["status"], "unresolved")
        self.assertEqual(result["reason"], "strong_evidence_conflict")
        self.assertEqual(result["candidate_audit"][0]["state"], "conflicted")
        self.assertIsNone(result["selected_sense_id"])

    def test_all_candidates_strongly_contradicted_returns_unresolved(self):
        result = select_contextual_sense(
            [candidate("K0001-S1"), candidate("K0001-S2")],
            [
                item("K0001-S1", "contradicts", rule_id="CE000001"),
                item("K0001-S2", "contradicts", rule_id="CE000002"),
            ],
        )
        self.assertEqual(result["status"], "unresolved")
        self.assertIsNone(result["selected_sense_id"])
        self.assertEqual(
            [entry["state"] for entry in result["candidate_audit"]],
            ["excluded", "excluded"],
        )

    def test_weak_evidence_never_accumulates_into_a_decision(self):
        evidence = []
        for index in range(5):
            evidence.append(item(
                "K0001-S1", "supports", "weak", f"CE{index + 1:06d}"
            ))
            evidence.append(item(
                "K0001-S2", "contradicts", "weak", f"CE{index + 101:06d}"
            ))
        result = select_contextual_sense(
            [candidate("K0001-S1"), candidate("K0001-S2")],
            evidence,
        )
        self.assertEqual(result["status"], "ambiguous")
        self.assertEqual(len(result["candidate_audit"][0]["weak_evidence"]), 5)
        self.assertEqual(len(result["candidate_audit"][1]["weak_evidence"]), 5)

    def test_evidence_for_unknown_sense_is_ignored_and_recorded(self):
        result = select_contextual_sense(
            [candidate("K0001-S1"), candidate("K0001-S2")],
            [item("K9999-S1", "contradicts")],
        )
        self.assertEqual(result["status"], "ambiguous")
        self.assertEqual(len(result["ignored_evidence"]), 1)
        self.assertEqual(
            result["ignored_evidence"][0]["ignored_reason"], "unknown_sense"
        )
        self.assertEqual(result["used_evidence"], [])

    def test_evidence_outside_this_token_candidate_group_cannot_exclude_candidate(self):
        # K0001-S1 and K0001-S2 belong to this occurrence; K0002-S1 is another.
        result = select_contextual_sense(
            [candidate("K0001-S1"), candidate("K0001-S2")],
            [
                item("K0001-S1", "supports", rule_id="CE000001"),
                item("K0002-S1", "contradicts", rule_id="CE000002"),
            ],
        )
        self.assertEqual(result["status"], "ambiguous")
        self.assertEqual(
            [entry["state"] for entry in result["candidate_audit"]],
            ["viable", "viable"],
        )
        self.assertEqual(len(result["ignored_evidence"]), 1)

    def test_candidate_metadata_and_all_candidate_evidence_are_preserved_in_audit(self):
        candidates = [
            candidate("K0001-S1", lemma="bisa"),
            candidate("K0001-S2", lemma="bisa"),
        ]
        evidence = [
            item("K0001-S1", "supports", rule_id="CE000001"),
            item("K0001-S2", "contradicts", rule_id="CE000002"),
            item("K0001-S2", "supports", "weak", "CE000003"),
        ]
        result = select_contextual_sense(candidates, evidence)
        self.assertEqual(result["status"], "selected")
        self.assertEqual(result["candidate_audit"][0]["candidate"]["lemma"], "bisa")
        self.assertEqual(
            result["candidate_audit"][1]["weak_evidence"][0]["rule_id"],
            "CE000003",
        )
        self.assertEqual(len(result["used_evidence"]), 3)
        self.assertEqual(len(result["candidate_audit"]), 2)

    def test_inputs_are_unchanged_and_output_is_deterministic(self):
        candidates = [candidate("K0001-S1"), candidate("K0001-S2")]
        evidence = [
            item("K0001-S1", "supports"),
            item("K0001-S2", "contradicts", rule_id="CE000002"),
        ]
        before = copy.deepcopy((candidates, evidence))
        first = select_contextual_sense(candidates, evidence)
        second = select_contextual_sense(candidates, evidence)
        self.assertEqual((candidates, evidence), before)
        self.assertEqual(first, second)

    def test_duplicate_candidates_and_invalid_evidence_are_rejected(self):
        with self.assertRaises(ContextualSenseSelectorError):
            select_contextual_sense(
                [candidate("K0001-S1"), candidate("K0001-S1")], []
            )
        with self.assertRaises(ContextualSenseSelectorError):
            select_contextual_sense(
                [candidate("K0001-S1")],
                [{"sense_id": "K0001-S1", "polarity": "maybe", "strength": "strong"}],
            )


if __name__ == "__main__":
    unittest.main()

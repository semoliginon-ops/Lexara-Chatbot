"""Exactly 11 focused unit tests for Clarification Planner v1."""
import copy
import unittest

from tools.clarification_planner import (
    ClarificationPlannerError,
    plan_clarification,
)


def ref(field="pos_candidates", token_index=0, candidate_index=0):
    return {
        "source_field": field,
        "token_index": token_index,
        "candidate_index": candidate_index,
    }


def item(status="ambiguous", refs=None, dimension="pos"):
    return {
        "dimension": dimension,
        "token_index": 0,
        "candidate_refs": refs if refs is not None else [
            ref(candidate_index=0), ref(candidate_index=1)
        ],
        "evidence_refs": [],
        "status": status,
        "reason": "test_fixture",
    }


def report(items=None, status="ambiguous", intent=None):
    value = {
        "schema_version": "1.0",
        "source": {"snapshot_status": "assembled", "parser_status": "parsed"},
        "ambiguity": {
            "status": status,
            "items": items if items is not None else [item()],
        },
        "communicative_intent": intent or {
            "status": "unresolved", "label": "unknown", "candidates": []
        },
    }
    return value


def opportunity(index=0, refs=None, material=True, distinguishable=True, priority=0):
    return {
        "ambiguity_item_index": index,
        "candidate_refs": refs if refs is not None else [
            ref(candidate_index=0), ref(candidate_index=1)
        ],
        "material_to_next_response": material,
        "user_can_distinguish": distinguishable,
        "priority": priority,
    }


class ClarificationPlannerTests(unittest.TestCase):
    def test_rejects_invalid_report_shape(self):
        with self.assertRaises(ClarificationPlannerError):
            plan_clarification({"ambiguity": "invalid"})
        with self.assertRaises(ClarificationPlannerError):
            plan_clarification({"ambiguity": {"status": "ambiguous", "items": "bad"}})

    def test_proceeds_when_there_are_no_ambiguity_items(self):
        result = plan_clarification(report(items=[], status="resolved"))
        self.assertEqual(result["decision"], "proceed")
        self.assertIsNone(result["focus"])

    def test_defers_when_ambiguity_report_is_deferred(self):
        result = plan_clarification(report(
            items=[item("deferred", refs=[])], status="deferred"
        ))
        self.assertEqual(result["decision"], "defer")
        self.assertIsNone(result["focus"])

    def test_does_not_ask_about_unresolved_syntax_without_candidates(self):
        result = plan_clarification(report(
            items=[item("unresolved", refs=[], dimension="syntax")],
            status="unresolved",
        ))
        self.assertEqual(result["decision"], "abstain")
        self.assertEqual(result["reason"], "no_valid_clarification_opportunity")

    def test_abstains_when_ambiguous_item_has_fewer_than_two_candidate_refs(self):
        result = plan_clarification(report(items=[
            item(refs=[ref("lexical_candidates", 0, 0)], dimension="lexical_sense")
        ]), [opportunity(refs=[ref("lexical_candidates", 0, 0)])])
        self.assertEqual(result["decision"], "abstain")

    def test_does_not_ask_when_uncertainty_is_not_material(self):
        result = plan_clarification(report(), [opportunity(material=False)])
        self.assertEqual(result["decision"], "proceed")
        self.assertIsNone(result["focus"])

    def test_does_not_ask_when_user_cannot_distinguish_candidates(self):
        result = plan_clarification(report(), [opportunity(distinguishable=False)])
        self.assertEqual(result["decision"], "proceed")
        self.assertIsNone(result["focus"])

    def test_asks_with_one_focus_for_valid_traceable_opportunity(self):
        source_refs = [ref(candidate_index=0), ref(candidate_index=1)]
        original = report(items=[item(refs=source_refs)])
        before = copy.deepcopy(original)
        result = plan_clarification(original, [opportunity(refs=source_refs)])
        self.assertEqual(result["decision"], "ask")
        self.assertEqual(result["focus"]["ambiguity_item_index"], 0)
        self.assertEqual(result["focus"]["candidate_refs"], source_refs)
        self.assertEqual(original, before)

    def test_selects_highest_priority_opportunity_and_only_one_focus(self):
        first_refs = [ref(candidate_index=0), ref(candidate_index=1)]
        second_refs = [
            ref("lexical_candidates", 1, 0),
            ref("lexical_candidates", 1, 1),
        ]
        result = plan_clarification(report(items=[
            item(refs=first_refs), item(refs=second_refs)
        ]), [
            opportunity(index=0, refs=first_refs, priority=5),
            opportunity(index=1, refs=second_refs, priority=1),
        ])
        self.assertEqual(result["decision"], "ask")
        self.assertEqual(result["focus"]["ambiguity_item_index"], 1)

    def test_coexisting_communicative_markers_do_not_trigger_clarification(self):
        result = plan_clarification(report(
            items=[], status="resolved",
            intent={
                "status": "ambiguous",
                "label": None,
                "candidates": ["question", "request"],
                "reason": "multiple_explicit_forms",
            },
        ))
        self.assertEqual(result["decision"], "proceed")

    def test_abstains_on_invalid_item_index_or_unmatched_candidate_reference(self):
        refs = [ref(candidate_index=0), ref(candidate_index=1)]
        bad_index = opportunity(index=4, refs=refs)
        bad_ref = opportunity(refs=[ref(candidate_index=0), ref(candidate_index=9)])
        malformed_ref = {**ref(candidate_index=9), "extra": []}
        bad_nested_ref = opportunity(refs=[ref(candidate_index=0), malformed_ref])
        self.assertEqual(
            plan_clarification(report(), [bad_index])["decision"], "abstain"
        )
        self.assertEqual(
            plan_clarification(report(), [bad_ref])["decision"], "abstain"
        )
        self.assertEqual(
            plan_clarification(report(), [bad_nested_ref])["decision"], "abstain"
        )


if __name__ == "__main__":
    unittest.main()

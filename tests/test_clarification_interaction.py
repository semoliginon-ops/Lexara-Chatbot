"""Exactly 10 focused tests for clarification presentation and response recording."""
import copy
import unittest

from tools.clarification_interaction import (
    prepare_clarification_prompt,
    record_clarification_response,
)


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


def parent_ref():
    return {
        "source_field": "lexical_candidates",
        "token_index": 0,
        "candidate_index": 0,
    }


def sense_ref(index, sense_id):
    return {
        **parent_ref(),
        "sense_index": index,
        "sense_id": sense_id,
    }


def make_plan():
    return {
        "schema_version": "1.1",
        "decision": "ask",
        "reason": "one_material_user_distinguishable_sense_ambiguity",
        "focus": {
            "ambiguity_item_index": 0,
            "parent_candidate_ref": parent_ref(),
            "sense_refs": [
                sense_ref(0, "K0016-S1"),
                sense_ref(1, "K0016-S2"),
            ],
        },
    }


def prepared_session():
    result = prepare_clarification_prompt(
        make_plan(), make_snapshot(), "local-session-001"
    )
    return result["session"]


class ClarificationInteractionTests(unittest.TestCase):
    def test_does_not_present_when_planner_did_not_request_ask(self):
        result = prepare_clarification_prompt(
            {"decision": "abstain", "focus": None},
            make_snapshot(),
            "local-session-001",
        )
        self.assertEqual(result["status"], "cannot_present_safely")
        self.assertIsNone(result["prompt"])

    def test_does_not_present_when_focus_is_missing_or_invalid(self):
        for plan in (
            {"decision": "ask", "focus": None},
            {"decision": "ask", "focus": "invalid"},
        ):
            result = prepare_clarification_prompt(
                plan, make_snapshot(), "local-session-001"
            )
            self.assertEqual(result["status"], "cannot_present_safely")

    def test_rejects_sense_references_that_do_not_match_snapshot(self):
        plan = make_plan()
        plan["focus"]["sense_refs"][1]["sense_id"] = "K9999-S2"
        result = prepare_clarification_prompt(
            plan, make_snapshot(), "local-session-001"
        )
        self.assertEqual(result["status"], "cannot_present_safely")

    def test_requires_two_distinct_trusted_descriptions(self):
        plan = make_plan()
        plan["focus"]["sense_refs"] = [sense_ref(0, "K0016-S1")]
        result = prepare_clarification_prompt(
            plan, make_snapshot(), "local-session-001"
        )
        self.assertEqual(result["status"], "cannot_present_safely")

        snapshot = make_snapshot()
        snapshot["tokens"][0]["lexical_candidates"][0]["entry"]["senses"][1]["definition"] = (
            snapshot["tokens"][0]["lexical_candidates"][0]["entry"]["senses"][0]["definition"]
        )
        result = prepare_clarification_prompt(
            make_plan(), snapshot, "local-session-001"
        )
        self.assertEqual(result["status"], "cannot_present_safely")

    def test_does_not_split_entry_candidate_without_sense_level_refs(self):
        plan = {
            "decision": "ask",
            "focus": {
                "ambiguity_item_index": 0,
                "candidate_refs": [parent_ref()],
            },
        }
        result = prepare_clarification_prompt(
            plan, make_snapshot(), "local-session-001"
        )
        self.assertEqual(result["status"], "cannot_present_safely")
        self.assertEqual(result["reason"], "sense_level_focus_required")

    def test_presents_one_neutral_prompt_using_source_definitions(self):
        snapshot = make_snapshot()
        before = copy.deepcopy(snapshot)
        result = prepare_clarification_prompt(
            make_plan(), snapshot, "local-session-001"
        )
        self.assertEqual(result["status"], "presented")
        self.assertEqual(
            result["prompt"]["text"],
            'Pada bagian "bangun", makna yang kamu maksud yang mana?',
        )
        self.assertEqual(
            [choice["label"] for choice in result["prompt"]["choices"]],
            [
                "Beralih dari keadaan tidur ke keadaan sadar.",
                "Berdiri atau menjadi tegak dari posisi duduk atau berbaring.",
            ],
        )
        self.assertTrue(result["prompt"]["allow_free_text"])
        self.assertTrue(result["prompt"]["allow_decline"])
        self.assertNotIn("K0016-S1", str(result["prompt"]))
        self.assertEqual(snapshot, before)

    def test_records_one_valid_choice_with_its_source_reference(self):
        session = prepared_session()
        result = record_clarification_response(
            session, {"type": "choice", "choice_key": "option_2"}
        )
        self.assertEqual(result["status"], "answered_choice")
        self.assertEqual(
            result["session"]["response"]["sense_ref"],
            sense_ref(1, "K0016-S2"),
        )
        self.assertEqual(session["status"], "presented")

    def test_preserves_free_text_without_forcing_a_candidate_mapping(self):
        session = prepared_session()
        raw_text = "Maksudku bangun dari duduk, tapi bukan berdiri penuh"
        result = record_clarification_response(
            session, {"type": "free_text", "text": raw_text}
        )
        self.assertEqual(result["status"], "answered_free_text")
        self.assertEqual(result["session"]["response"]["text"], raw_text)
        self.assertEqual(result["session"]["response"]["completeness"], "unknown")
        self.assertNotIn("sense_ref", result["session"]["response"])

    def test_records_decline_and_no_response_without_selecting_a_sense(self):
        declined = record_clarification_response(
            prepared_session(), {"type": "decline"}
        )
        no_response = record_clarification_response(
            prepared_session(), {"type": "no_response"}
        )
        self.assertEqual(declined["status"], "declined")
        self.assertEqual(no_response["status"], "no_response")
        self.assertIsNone(declined["session"]["response"].get("sense_ref"))
        self.assertIsNone(no_response["session"]["response"].get("sense_ref"))

    def test_invalid_or_multiple_choices_do_not_select_automatically(self):
        for response in (
            {"type": "choice", "choice_key": "unknown_option"},
            {"type": "choices", "choice_keys": ["option_1", "option_2"]},
        ):
            result = record_clarification_response(prepared_session(), response)
            self.assertEqual(result["status"], "invalid_response")
            self.assertIsNone(result["session"]["response"])


if __name__ == "__main__":
    unittest.main()

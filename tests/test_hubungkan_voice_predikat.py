"""Tests for conservative predicate-head and token-level voice connection."""
import unittest

from tools.hubungkan_voice_predikat import connect_predicate_voice


def parsed(head="menulis", status="parsed", method="conservative_svo_v4"):
    return {
        "parser_method": method,
        "status": status,
        "predicate_structure": {"head": head, "modifiers": []},
    }


def analysis(*tokens):
    return {"tokens": list(tokens)}


def word(token, voice_status="identified", voice="active", reason=None):
    return {
        "token": token,
        "kind": "word",
        "voice_analysis": {
            "status": voice_status,
            "voice": voice if voice_status == "identified" else None,
            "reason": reason or ("dictionary_validated_voice_morphology" if voice_status == "identified" else "no_confirmed_voice_morphology"),
            "evidence": [{"voice": voice}] if voice_status == "identified" else [],
        },
    }


class PredicateVoiceConnectionTests(unittest.TestCase):
    def test_connects_active_voice_from_unique_predicate_head(self):
        result = connect_predicate_voice(
            parsed("menulis"),
            analysis(word("Rina"), word("menulis"), word("surat")),
        )
        self.assertEqual(result["status"], "identified")
        self.assertEqual(result["voice"], "active")
        self.assertEqual(result["predicate_head"], "menulis")
        self.assertEqual(result["token_index"], 1)

    def test_connects_passive_voice_from_unique_predicate_head(self):
        result = connect_predicate_voice(
            parsed("ditulis"),
            analysis(word("surat"), word("ditulis", voice="passive"), word("Rina")),
        )
        self.assertEqual(result["status"], "identified")
        self.assertEqual(result["voice"], "passive")
        self.assertEqual(result["token_index"], 1)

    def test_does_not_guess_when_predicate_form_occurs_more_than_once(self):
        result = connect_predicate_voice(
            parsed("menulis"),
            analysis(word("menulis"), word("Rina"), word("menulis")),
        )
        self.assertEqual(result["status"], "unresolved")
        self.assertEqual(result["reason"], "predicate_head_token_alignment_ambiguous")

    def test_does_not_connect_partial_parse(self):
        result = connect_predicate_voice(
            parsed(status="partial"),
            analysis(word("menulis")),
        )
        self.assertEqual(result["reason"], "parser_not_fully_resolved")

    def test_does_not_connect_clause_tree(self):
        result = connect_predicate_voice(
            parsed(method="conservative_coordination_v2"),
            analysis(word("menulis")),
        )
        self.assertEqual(result["reason"], "non_flat_clause_structure")

    def test_does_not_connect_when_token_voice_is_unresolved(self):
        result = connect_predicate_voice(
            parsed("terbuka"),
            analysis(word("terbuka", voice_status="unresolved")),
        )
        self.assertEqual(result["status"], "unresolved")
        self.assertEqual(result["reason"], "no_confirmed_voice_morphology")

    def test_does_not_connect_when_head_is_missing_from_token_analysis(self):
        result = connect_predicate_voice(
            parsed("menulis"),
            analysis(word("Rina"), word("surat")),
        )
        self.assertEqual(result["reason"], "predicate_head_not_found_in_token_analysis")

    def test_requires_dictionary_arguments(self):
        with self.assertRaises(TypeError):
            connect_predicate_voice([], {})
        with self.assertRaises(TypeError):
            connect_predicate_voice({}, [])

    def test_requires_token_array(self):
        with self.assertRaises(ValueError):
            connect_predicate_voice(parsed(), {})


if __name__ == "__main__":
    unittest.main()

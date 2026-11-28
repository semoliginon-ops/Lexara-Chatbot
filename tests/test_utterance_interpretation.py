import unittest

from tools.utterance_interpretation import (
    UtteranceInterpretationError,
    interpret_utterance,
)


def snapshot(text="", tokens=None, status="assembled", parser_status="parsed"):
    return {
        "status": status,
        "normalized_text": text,
        "parser_status": parser_status,
        "tokens": tokens or [],
        "parser_result": {"status": parser_status, "roles": {}},
    }


def word(token, **extra):
    value = {
        "token": token,
        "kind": "word",
        "lexical_status": "matched",
        "lexical_candidates": [],
        "pos_candidates": [],
        "pos": [],
        "pos_status": "identified",
        "syntactic_role": None,
        "syntax_status": "mapped",
        "syntax_reason": None,
    }
    value.update(extra)
    return value


class UtteranceInterpretationTests(unittest.TestCase):
    def test_rejects_invalid_snapshot_shape(self):
        with self.assertRaises(UtteranceInterpretationError):
            interpret_utterance({"tokens": "not-a-list"})
        with self.assertRaises(UtteranceInterpretationError):
            interpret_utterance({"tokens": [{"token": 42}]})

    def test_preserves_original_snapshot_and_parser_status(self):
        result = interpret_utterance(snapshot(
            "Aku pulang.", [word("Aku")], status="partial", parser_status="partial"
        ))
        self.assertEqual(result["source"], {
            "snapshot_status": "partial", "parser_status": "partial"
        })

    def test_records_multiple_lexical_senses_by_source_index(self):
        result = interpret_utterance(snapshot(tokens=[word(
            "bisa",
            lexical_candidates=[{"lemma": "bisa", "sense_ids": ["S1", "S2"]}],
        )]))
        item = result["ambiguity"]["items"][0]
        self.assertEqual(item["dimension"], "lexical_sense")
        self.assertEqual(item["candidate_refs"][0]["candidate_index"], 0)
        self.assertEqual(item["candidate_refs"][0]["source_field"], "lexical_candidates")

    def test_records_multiple_pos_candidates_by_source_index(self):
        result = interpret_utterance(snapshot(tokens=[word(
            "bisa",
            pos_candidates=[{"pos": ["VERB"]}, {"pos": ["NOUN"]}],
            pos=["VERB", "NOUN"],
        )]))
        item = result["ambiguity"]["items"][0]
        self.assertEqual(item["dimension"], "pos")
        self.assertEqual(
            [ref["candidate_index"] for ref in item["candidate_refs"]], [0, 1]
        )

    def test_preserves_parser_unresolved_without_assigning_role(self):
        result = interpret_utterance(snapshot(tokens=[word(
            "entitas", syntax_status="unresolved",
            syntax_reason="parser_reports_token_unresolved",
        )]))
        item = result["ambiguity"]["items"][0]
        self.assertEqual(item["status"], "unresolved")
        self.assertEqual(item["dimension"], "syntax")

    def test_preserves_deferred_syntax_without_guessing(self):
        result = interpret_utterance(snapshot(tokens=[word(
            "dia", syntax_status="deferred",
            syntax_reason="repeated_source_token",
        )]))
        self.assertEqual(result["ambiguity"]["status"], "deferred")
        self.assertEqual(result["ambiguity"]["items"][0]["status"], "deferred")

    def test_not_observed_alone_does_not_create_ambiguity(self):
        result = interpret_utterance(snapshot(tokens=[word(
            "mungkin", syntax_status="not_observed",
            syntax_reason="parser_has_no_observation_for_token",
        )]))
        self.assertEqual(result["ambiguity"]["items"], [])
        self.assertEqual(result["ambiguity"]["status"], "resolved")

    def test_recognizes_explicit_question_mark(self):
        result = interpret_utterance(snapshot("Kamu pulang?"))
        self.assertEqual(result["communicative_intent"]["label"], "question")
        self.assertEqual(result["communicative_intent"]["reason"], "explicit_question_mark")

    def test_recognizes_explicit_request_marker(self):
        result = interpret_utterance(snapshot(tokens=[word("tolong"), word("buka")]))
        self.assertEqual(result["communicative_intent"]["label"], "request")

    def test_recognizes_explicit_prohibition_marker(self):
        result = interpret_utterance(snapshot(tokens=[word("jangan"), word("pergi")]))
        self.assertEqual(result["communicative_intent"]["label"], "directive")

    def test_unknown_without_supported_explicit_marker(self):
        result = interpret_utterance(snapshot(
            "Aku pulang.", [word("aku"), word("pulang")]
        ))
        intent = result["communicative_intent"]
        self.assertEqual(intent["label"], "unknown")
        self.assertEqual(intent["status"], "unresolved")


if __name__ == "__main__":
    unittest.main()

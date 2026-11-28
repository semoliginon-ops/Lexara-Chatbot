import unittest

from tools.utterance_interpretation import interpret_utterance


def make_snapshot(text="", tokens=None):
    return {
        "status": "assembled",
        "normalized_text": text,
        "parser_status": "parsed",
        "tokens": [
            {"token": token, "kind": "word"}
            for token in (tokens or [])
        ],
    }


class CoexistingExplicitIntentTests(unittest.TestCase):
    def test_question_and_request_are_reported_as_coexisting(self):
        intent = interpret_utterance(
            make_snapshot("Tolong buka pintu?", ["tolong", "buka", "pintu"])
        )["communicative_intent"]
        self.assertEqual(intent["status"], "resolved")
        self.assertIsNone(intent["label"])
        self.assertEqual(intent["labels"], ["question", "request"])
        self.assertEqual(intent["candidates"], [])
        self.assertEqual(intent["evidence_refs"], [
            {"source_field": "normalized_text"},
            {"source_field": "tokens", "token_index": 0},
        ])
        self.assertEqual(intent["reason"], "multiple_coexisting_explicit_forms")

    def test_request_and_directive_are_both_preserved(self):
        intent = interpret_utterance(
            make_snapshot("", ["tolong", "jangan", "pergi"])
        )["communicative_intent"]
        self.assertEqual(intent["status"], "resolved")
        self.assertEqual(intent["labels"], ["request", "directive"])
        self.assertEqual(intent["evidence_refs"], [
            {"source_field": "tokens", "token_index": 0},
            {"source_field": "tokens", "token_index": 1},
        ])

    def test_single_marker_keeps_legacy_fields(self):
        intent = interpret_utterance(
            make_snapshot("", ["tolong", "buka"])
        )["communicative_intent"]
        self.assertEqual(intent["status"], "resolved")
        self.assertEqual(intent["label"], "request")
        self.assertEqual(intent["labels"], ["request"])
        self.assertEqual(intent["candidates"], ["request"])

    def test_no_marker_remains_unknown(self):
        intent = interpret_utterance(
            make_snapshot("Aku pulang.", ["aku", "pulang"])
        )["communicative_intent"]
        self.assertEqual(intent["status"], "unresolved")
        self.assertEqual(intent["label"], "unknown")
        self.assertEqual(intent["labels"], [])
        self.assertEqual(intent["candidates"], [])


if __name__ == "__main__":
    unittest.main()

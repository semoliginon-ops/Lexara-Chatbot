"""Regression tests for the conservative simple-clause parser."""
import unittest

from tools.parser_kalimat import parse_sentence


def token(value, pos=None, *, status=None, context=None, context_status=None, punctuation=False):
    return {
        "token": value,
        "kind": "punctuation" if punctuation else "word",
        "pos": list(pos or []),
        "pos_status": status or ("not_applicable" if punctuation else "identified" if len(pos or []) == 1 else "ambiguous"),
        "context_pos": context,
        "pos_context_status": context_status,
    }


def analysis(*items):
    return {"tokens": list(items)}


class SimpleClauseParserTests(unittest.TestCase):
    def test_parses_subject_predicate_object(self):
        result = parse_sentence(analysis(
            token("dia", ["PRON"]),
            token("makan", ["VERB"]),
            token("nasi", ["NOUN"]),
            token(".", punctuation=True),
        ))
        self.assertEqual(result["status"], "parsed")
        self.assertEqual(result["pattern"], "S-P-O")
        self.assertEqual(result["roles"]["subject"], ["dia"])
        self.assertEqual(result["roles"]["predicate"], ["makan"])
        self.assertEqual(result["roles"]["object"], ["nasi"])

    def test_parses_adverbial_predicate_and_prepositional_adjunct(self):
        result = parse_sentence(analysis(
            token("aku", ["PRON"]),
            token("sedang", ["ADV"]),
            token("bekerja", ["VERB"]),
            token("di", ["PREP"]),
            token("rumah", ["NOUN"]),
            token(".", punctuation=True),
        ))
        self.assertEqual(result["status"], "parsed")
        self.assertEqual(result["pattern"], "S-P-K")
        self.assertEqual(result["roles"]["subject"], ["aku"])
        self.assertEqual(result["roles"]["predicate"], ["sedang", "bekerja"])
        self.assertEqual(
            result["roles"]["adjuncts"],
            [{"preposition": "di", "phrase": ["rumah"]}],
        )

    def test_uses_contextual_pos_only_when_selected(self):
        result = parse_sentence(analysis(
            token("aku", ["PRON"]),
            token("sedang", ["ADV"]),
            token("jalan", ["NOUN", "VERB"], status="identified",
                  context="VERB", context_status="selected_by_context"),
        ))
        self.assertEqual(result["roles"]["predicate"], ["sedang", "jalan"])

    def test_does_not_force_ambiguous_subject(self):
        result = parse_sentence(analysis(
            token("jalan", ["NOUN", "VERB"], status="ambiguous"),
            token("makan", ["VERB"]),
            token("nasi", ["NOUN"]),
        ))
        self.assertEqual(result["status"], "unresolved")
        self.assertIsNone(result["pattern"])
        self.assertEqual(result["roles"]["subject"], [])

    def test_returns_unresolved_when_no_certain_verb(self):
        result = parse_sentence(analysis(
            token("rumah", ["NOUN"]),
            token("besar", ["ADJ"]),
        ))
        self.assertEqual(result["status"], "unresolved")
        self.assertIn("Predikat VERB yang pasti belum ditemukan.", result["notes"])

    def test_internal_comma_is_not_misparsed_as_one_clause(self):
        result = parse_sentence(analysis(
            token("aku", ["PRON"]),
            token("makan", ["VERB"]),
            token(",", punctuation=True),
            token("dia", ["PRON"]),
            token("tidur", ["VERB"]),
        ))
        self.assertEqual(result["status"], "unsupported")
        self.assertIsNone(result["pattern"])

    def test_rejects_invalid_input(self):
        with self.assertRaises(TypeError):
            parse_sentence([])
        with self.assertRaises(ValueError):
            parse_sentence({})


if __name__ == "__main__":
    unittest.main()

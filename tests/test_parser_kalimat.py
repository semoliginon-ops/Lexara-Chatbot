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

    def test_parses_fronted_prepositional_adjunct_before_subject(self):
        result = parse_sentence(analysis(
            token("di", ["PREP"]),
            token("rumah", ["NOUN"]),
            token("aku", ["PRON"]),
            token("bekerja", ["VERB"]),
        ))
        self.assertEqual(result["status"], "parsed")
        self.assertEqual(result["pattern"], "S-P-K")
        self.assertEqual(result["roles"]["subject"], ["aku"])
        self.assertEqual(result["roles"]["predicate"], ["bekerja"])
        self.assertEqual(
            result["roles"]["adjuncts"],
            [{"preposition": "di", "phrase": ["rumah"]}],
        )

    def test_does_not_absorb_unclassified_prefix_as_fronted_adjunct(self):
        result = parse_sentence(analysis(
            token("mungkin", ["ADV"]),
            token("aku", ["PRON"]),
            token("bekerja", ["VERB"]),
        ))
        self.assertEqual(result["status"], "partial")
        self.assertIn("mungkin", result["unresolved_tokens"])

    def test_collects_simple_subject_phrase_with_number_and_adjective(self):
        result = parse_sentence(analysis(
            token("tiga", ["NUM"]),
            token("anak", ["NOUN"]),
            token("kecil", ["ADJ"]),
            token("makan", ["VERB"]),
            token("nasi", ["NOUN"]),
        ))
        self.assertEqual(result["status"], "parsed")
        self.assertEqual(result["pattern"], "S-P-O")
        self.assertEqual(result["roles"]["subject"], ["tiga", "anak", "kecil"])
        self.assertEqual(result["roles"]["object"], ["nasi"])

    def test_collects_simple_object_phrase_with_adjective(self):
        result = parse_sentence(analysis(
            token("dia", ["PRON"]),
            token("membeli", ["VERB"]),
            token("baju", ["NOUN"]),
            token("baru", ["ADJ"]),
        ))
        self.assertEqual(result["status"], "parsed")
        self.assertEqual(result["roles"]["object"], ["baju", "baru"])

    def test_includes_verbal_negation_in_predicate(self):
        result = parse_sentence(analysis(
            token("kami", ["PRON"]),
            token("tidak", ["ADV"]),
            token("membeli", ["VERB"]),
            token("ikan", ["NOUN"]),
        ))
        self.assertEqual(result["status"], "parsed")
        self.assertEqual(result["pattern"], "S-P-O")
        self.assertEqual(result["roles"]["predicate"], ["tidak", "membeli"])
        self.assertEqual(result["roles"]["object"], ["ikan"])

    def test_includes_temporal_negation_belum_in_predicate(self):
        result = parse_sentence(analysis(
            token("kami", ["PRON"]),
            token("belum", ["ADV"]),
            token("makan", ["VERB"]),
            token("nasi", ["NOUN"]),
        ))
        self.assertEqual(result["roles"]["predicate"], ["belum", "makan"])

    def test_groups_mau_before_lexical_verb_as_one_predicate(self):
        result = parse_sentence(analysis(
            token("aku", ["PRON"]),
            token("mau", ["VERB"]),
            token("pergi", ["VERB"]),
        ))
        self.assertEqual(result["status"], "parsed")
        self.assertEqual(result["pattern"], "S-P")
        self.assertEqual(result["roles"]["subject"], ["aku"])
        self.assertEqual(result["roles"]["predicate"], ["mau", "pergi"])

    def test_groups_ingin_before_lexical_verb_and_keeps_object(self):
        result = parse_sentence(analysis(
            token("dia", ["PRON"]),
            token("ingin", ["VERB"]),
            token("makan", ["VERB"]),
            token("nasi", ["NOUN"]),
        ))
        self.assertEqual(result["status"], "parsed")
        self.assertEqual(result["pattern"], "S-P-O")
        self.assertEqual(result["roles"]["predicate"], ["ingin", "makan"])
        self.assertEqual(result["roles"]["object"], ["nasi"])

    def test_modal_verb_standing_alone_remains_predicate(self):
        result = parse_sentence(analysis(
            token("aku", ["PRON"]),
            token("mau", ["VERB"]),
        ))
        self.assertEqual(result["status"], "parsed")
        self.assertEqual(result["roles"]["predicate"], ["mau"])

    def test_parses_adjectival_predicate_after_pronoun_subject(self):
        result = parse_sentence(analysis(
            token("dia", ["PRON"]),
            token("sakit", ["ADJ"]),
        ))
        self.assertEqual(result["status"], "parsed")
        self.assertEqual(result["pattern"], "S-P")
        self.assertEqual(result["roles"]["subject"], ["dia"])
        self.assertEqual(result["roles"]["predicate"], ["sakit"])

    def test_parses_adjectival_predicate_after_demonstrative_subject(self):
        result = parse_sentence(analysis(
            token("rumah", ["NOUN"]),
            token("itu", ["PRON"]),
            token("besar", ["ADJ"]),
        ))
        self.assertEqual(result["status"], "parsed")
        self.assertEqual(result["roles"]["subject"], ["rumah", "itu"])
        self.assertEqual(result["roles"]["predicate"], ["besar"])

    def test_parses_simple_nominal_predicate(self):
        result = parse_sentence(analysis(
            token("ayah", ["NOUN"]),
            token("seorang", ["NUM"]),
            token("guru", ["NOUN"]),
        ))
        self.assertEqual(result["status"], "parsed")
        self.assertEqual(result["pattern"], "S-P")
        self.assertEqual(result["roles"]["subject"], ["ayah"])
        self.assertEqual(result["roles"]["predicate"], ["seorang", "guru"])

    def test_menjadi_takes_nominal_predicate_complement(self):
        result = parse_sentence(analysis(
            token("dia", ["PRON"]),
            token("menjadi", ["VERB"]),
            token("dokter", ["NOUN"]),
        ))
        self.assertEqual(result["status"], "parsed")
        self.assertEqual(result["pattern"], "S-P-Pel")
        self.assertEqual(result["roles"]["predicate"], ["menjadi"])
        self.assertEqual(result["roles"]["object"], [])
        self.assertEqual(result["roles"]["complement"], ["dokter"])

    def test_tampak_takes_adjectival_predicate_complement(self):
        result = parse_sentence(analysis(
            token("mereka", ["PRON"]),
            token("tampak", ["VERB"]),
            token("bahagia", ["ADJ"]),
        ))
        self.assertEqual(result["status"], "parsed")
        self.assertEqual(result["pattern"], "S-P-Pel")
        self.assertEqual(result["roles"]["object"], [])
        self.assertEqual(result["roles"]["complement"], ["bahagia"])

    def test_ordinary_transitive_verb_keeps_nominal_object(self):
        result = parse_sentence(analysis(
            token("dia", ["PRON"]),
            token("membeli", ["VERB"]),
            token("baju", ["NOUN"]),
        ))
        self.assertEqual(result["status"], "parsed")
        self.assertEqual(result["pattern"], "S-P-O")
        self.assertEqual(result["roles"]["object"], ["baju"])
        self.assertEqual(result["roles"]["complement"], [])

    def test_does_not_guess_ambiguous_noun_adjective_sequence(self):
        result = parse_sentence(analysis(
            token("rumah", ["NOUN"]),
            token("besar", ["ADJ"]),
        ))
        self.assertEqual(result["status"], "unresolved")
        self.assertIsNone(result["pattern"])

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
        self.assertIn("Predikat VERB atau pola predikat nonverbal sederhana", result["notes"][0])

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

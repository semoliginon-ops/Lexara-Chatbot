"""Regression tests for conservative contextual POS disambiguation."""
import unittest
from tools.analisis_teks import analyze_text
from tools.pencocokan_kamus import build_lexicon
from tools.pos_tagger import tag_pos
from tools.pos_context import disambiguate_pos_context


def entry(entry_id, lemma, pos, senses=None):
    return {
        "id": entry_id, "lemma": lemma, "pos": pos,
        "senses": senses or [{"sense_id": f"{entry_id}-S1", "definition": "Makna."}],
        "register": ["neutral"], "variants": [], "derived_forms": [],
    }


class ContextualPosTests(unittest.TestCase):
    def setUp(self):
        self.entries = [
            entry("K0001", "jalan", ["NOUN", "VERB"]),
            entry("K0002", "bisa", ["VERB", "NOUN"], [
                {"sense_id": "K0002-S1", "definition": "Mampu.", "pos": "VERB"},
                {"sense_id": "K0002-S2", "definition": "Racun.", "pos": "NOUN"},
            ]),
            entry("K0003", "makan", ["VERB"]), entry("K0004", "ular", ["NOUN"]),
            entry("K0005", "sedang", ["ADV"]), entry("K0006", "di", ["PREP"]),
            entry("K0007", "itu", ["PRON"]), entry("K0008", "aku", ["PRON"]),
            entry("K0009", "rajin", ["ADJ"]), entry("K0010", "disiplin", ["NOUN", "ADJ"]),
        ]
        self.lexicon = build_lexicon(self.entries)

    def analyze(self, text):
        return disambiguate_pos_context(tag_pos(analyze_text(text, self.lexicon)))

    def token(self, result, value):
        return next(item for item in result["tokens"] if item["token"] == value)

    def test_aspect_cue_selects_verb(self):
        token = self.token(self.analyze("sedang jalan"), "jalan")
        self.assertEqual(token["context_pos"], "VERB")
        self.assertEqual(token["pos_context_status"], "selected_by_context")

    def test_preposition_selects_noun(self):
        self.assertEqual(self.token(self.analyze("di jalan"), "jalan")["context_pos"], "NOUN")

    def test_demonstrative_selects_noun(self):
        self.assertEqual(self.token(self.analyze("jalan itu"), "jalan")["context_pos"], "NOUN")

    def test_bisa_before_verb_selects_verb(self):
        self.assertEqual(self.token(self.analyze("bisa makan"), "bisa")["context_pos"], "VERB")

    def test_bisa_before_noun_selects_noun(self):
        self.assertEqual(self.token(self.analyze("bisa ular"), "bisa")["context_pos"], "NOUN")

    def test_coordination_with_previous_adjective_selects_adjective(self):
        result = self.analyze("Dia sangat rajin dan disiplin")
        token = self.token(result, "disiplin")
        self.assertEqual(token["pos"], ["NOUN", "ADJ"])
        self.assertEqual(token["context_pos"], "ADJ")
        self.assertEqual(token["pos_context_status"], "selected_by_context")
        self.assertEqual(token["pos_context_evidence"][0]["rule"], "coordination_with_previous_conjunct")

    def test_ambiguous_without_cue_remains_unresolved(self):
        token = self.token(self.analyze("jalan"), "jalan")
        self.assertIsNone(token["context_pos"])
        self.assertEqual(token["pos_context_status"], "ambiguous")

    def test_conflicting_cues_remain_unresolved(self):
        token = self.token(self.analyze("sedang jalan itu"), "jalan")
        self.assertIsNone(token["context_pos"])
        self.assertEqual(token["pos_context_status"], "ambiguous")

    def test_original_lexical_pos_is_preserved(self):
        self.assertEqual(self.token(self.analyze("sedang jalan"), "jalan")["pos"], ["NOUN", "VERB"])

    def test_single_pos_is_marked_unambiguous(self):
        token = self.token(self.analyze("aku"), "aku")
        self.assertEqual(token["context_pos"], "PRON")
        self.assertEqual(token["pos_context_status"], "unambiguous")

    def test_unknown_word_remains_unknown(self):
        token = self.token(self.analyze("xyzabc"), "xyzabc")
        self.assertIsNone(token["context_pos"])
        self.assertEqual(token["pos_context_status"], "unknown")

    def test_punctuation_is_not_applicable(self):
        self.assertEqual(self.token(self.analyze("!"), "!")["pos_context_status"], "not_applicable")

    def test_rejects_non_dictionary_input(self):
        with self.assertRaises(TypeError):
            disambiguate_pos_context([])

    def test_rejects_missing_tokens(self):
        with self.assertRaises(ValueError):
            disambiguate_pos_context({})


if __name__ == "__main__":
    unittest.main()

"""Regression tests for lexicon-based POS tagging."""
import unittest

from tools.analisis_teks import analyze_text
from tools.pencocokan_kamus import build_lexicon
from tools.pos_tagger import tag_pos


def entry(entry_id, lemma, pos, senses=None, derived_forms=None):
    return {
        "id": entry_id,
        "lemma": lemma,
        "pos": pos,
        "senses": senses or [
            {"sense_id": f"{entry_id}-S1", "definition": "Makna."}
        ],
        "register": ["neutral"],
        "variants": [],
        "derived_forms": derived_forms or [],
    }


class PosTaggerTests(unittest.TestCase):
    def setUp(self):
        self.entries = [
            entry("K0001", "makan", ["VERB"], derived_forms=["makanan"]),
            entry("K0002", "bisa", ["VERB", "NOUN"], [
                {"sense_id": "K0002-S1", "definition": "Mampu.", "pos": "VERB"},
                {"sense_id": "K0002-S2", "definition": "Racun.", "pos": "NOUN"},
            ]),
            entry("K0003", "jalan", ["NOUN", "VERB"]),
            entry("K0004", "gue", ["PRON"]),
        ]
        self.lexicon = build_lexicon(self.entries)

    def analyze_and_tag(self, text):
        return tag_pos(analyze_text(text, self.lexicon))

    def test_identifies_entry_pos(self):
        result = self.analyze_and_tag("gue")
        token = result["tokens"][0]
        self.assertEqual(token["pos"], ["PRON"])
        self.assertEqual(token["pos_status"], "identified")

    def test_preserves_multiple_pos_on_one_entry(self):
        token = self.analyze_and_tag("jalan")["tokens"][0]
        self.assertEqual(token["pos"], ["NOUN", "VERB"])

    def test_preserves_sense_specific_pos(self):
        token = self.analyze_and_tag("bisa")["tokens"][0]
        senses = token["pos_candidates"][0]["senses"]
        self.assertEqual([s["pos"] for s in senses], [["VERB"], ["NOUN"]])

    def test_does_not_choose_between_ambiguous_pos(self):
        token = self.analyze_and_tag("bisa")["tokens"][0]
        self.assertEqual(token["pos"], ["VERB", "NOUN"])
        self.assertFalse(self.analyze_and_tag("bisa")["pos_contextual_disambiguation"])

    def test_does_not_inherit_lemma_pos_for_derived_form(self):
        token = self.analyze_and_tag("makanan")["tokens"][0]
        self.assertEqual(token["pos"], [])
        self.assertEqual(token["pos_status"], "requires_morphology")

    def test_unknown_word_has_unknown_status(self):
        token = self.analyze_and_tag("xyzabc")["tokens"][0]
        self.assertEqual(token["pos"], [])
        self.assertEqual(token["pos_status"], "unknown")

    def test_punctuation_is_not_applicable(self):
        token = self.analyze_and_tag("!")["tokens"][0]
        self.assertEqual(token["pos_status"], "not_applicable")

    def test_preserves_original_analysis_fields(self):
        original = analyze_text("gue makan", self.lexicon)
        tagged = tag_pos(original)
        self.assertEqual(tagged["normalized_text"], original["normalized_text"])
        self.assertEqual(
            [t["token"] for t in tagged["tokens"]],
            [t["token"] for t in original["tokens"]],
        )

    def test_rejects_non_dictionary_input(self):
        with self.assertRaises(TypeError):
            tag_pos([])

    def test_rejects_missing_tokens(self):
        with self.assertRaises(ValueError):
            tag_pos({})


if __name__ == "__main__":
    unittest.main()

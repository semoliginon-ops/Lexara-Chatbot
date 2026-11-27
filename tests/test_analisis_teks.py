"""Regression tests for tools.analisis_teks."""
import unittest

from tools.analisis_teks import analyze_text
from tools.pencocokan_kamus import build_lexicon


def entry(entry_id, lemma, **extra):
    result = {
        "id": entry_id,
        "lemma": lemma,
        "pos": ["VERB"],
        "senses": [{"sense_id": f"{entry_id}-S1", "definition": "Makna."}],
        "register": ["neutral"],
        "variants": [],
        "derived_forms": [],
    }
    result.update(extra)
    return result


class TextAnalysisTests(unittest.TestCase):
    def setUp(self):
        self.entries = [
            entry("K0001", "makan", derived_forms=["memakan"]),
            entry("K0002", "gue", variants=["gw"]),
            entry("K0003", "bisa"),
            entry("K0004", "bisa"),
            entry("K0005", "tulis"),
            entry("K0006", "buka"),
        ]
        self.lexicon = build_lexicon(self.entries)

    def test_combines_normalization_tokenization_and_lookup(self):
        result = analyze_text("  GUE mau MAKAN!  ", self.lexicon)
        self.assertEqual(result["normalized_text"], "gue mau makan!")
        self.assertEqual([item["token"] for item in result["tokens"]],
                         ["gue", "mau", "makan", "!"])
        self.assertEqual(result["tokens"][0]["status"], "matched")
        self.assertEqual(result["tokens"][1]["status"], "unknown")
        self.assertEqual(result["tokens"][2]["candidates"][0]["lemma"], "makan")

    def test_token_analysis_exposes_passive_morphological_voice_evidence(self):
        result = analyze_text("ditulis", self.lexicon)
        token = result["tokens"][0]
        self.assertEqual(token["voice_analysis"]["status"], "identified")
        self.assertEqual(token["voice_analysis"]["voice"], "passive")

    def test_token_analysis_exposes_active_morphological_voice_evidence(self):
        result = analyze_text("menulis", self.lexicon)
        token = result["tokens"][0]
        self.assertEqual(token["voice_analysis"]["status"], "identified")
        self.assertEqual(token["voice_analysis"]["voice"], "active")

    def test_token_analysis_keeps_ambiguous_ter_form_unresolved(self):
        result = analyze_text("terbuka", self.lexicon)
        token = result["tokens"][0]
        self.assertEqual(token["voice_analysis"]["status"], "unresolved")
        self.assertIsNone(token["voice_analysis"]["voice"])

    def test_matches_variant(self):
        result = analyze_text("gw", self.lexicon)
        self.assertEqual(result["tokens"][0]["candidates"][0]["match_type"], "variant")

    def test_matches_recorded_derived_form(self):
        result = analyze_text("memakan", self.lexicon)
        self.assertEqual(result["tokens"][0]["candidates"][0]["match_type"], "derived_form")

    def test_preserves_all_ambiguous_candidates(self):
        result = analyze_text("bisa", self.lexicon)
        self.assertEqual(len(result["tokens"][0]["candidates"]), 2)

    def test_punctuation_is_preserved_and_not_looked_up(self):
        result = analyze_text("(halo)!!", self.lexicon)
        punctuation = [item for item in result["tokens"] if item["kind"] == "punctuation"]
        self.assertEqual([item["token"] for item in punctuation], ["(", ")", "!", "!"])
        self.assertTrue(all(item["status"] == "not_applicable" for item in punctuation))

    def test_empty_input(self):
        self.assertEqual(analyze_text("  ", self.lexicon)["tokens"], [])

    def test_rejects_non_string_text(self):
        with self.assertRaises(TypeError):
            analyze_text(None, self.lexicon)

    def test_rejects_non_dictionary_lexicon(self):
        with self.assertRaises(TypeError):
            analyze_text("makan", [])

if __name__ == "__main__":
    unittest.main()

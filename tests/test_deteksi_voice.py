"""Regression tests for conservative morphological voice detection."""
import unittest

from tools.deteksi_voice import detect_voice
from tools.morfologi import analyze_morphology
from tools.pencocokan_kamus import build_lexicon


def entry(entry_id, lemma, pos=("VERB",)):
    return {
        "id": entry_id,
        "lemma": lemma,
        "pos": list(pos),
        "senses": [{"sense_id": f"{entry_id}-S1", "definition": "Makna uji."}],
        "register": ["neutral"],
        "variants": [],
        "derived_forms": [],
    }


class VoiceDetectionTests(unittest.TestCase):
    def setUp(self):
        self.lexicon = build_lexicon([
            entry("K0001", "tulis"),
            entry("K0002", "buka"),
            entry("K0003", "ambil"),
            entry("K0004", "lari"),
            entry("K0005", "terima", ("VERB", "NOUN")),
        ])

    def analyze(self, word):
        return analyze_morphology(word, self.lexicon)

    def test_di_prefix_identifies_passive(self):
        result = detect_voice(self.analyze("ditulis"))
        self.assertEqual(result["status"], "identified")
        self.assertEqual(result["voice"], "passive")

    def test_nested_di_prefix_identifies_passive(self):
        result = detect_voice(self.analyze("dibukakan"))
        self.assertEqual(result["voice"], "passive")

    def test_men_prefix_identifies_active(self):
        result = detect_voice(self.analyze("menulis"))
        self.assertEqual(result["voice"], "active")

    def test_mem_prefix_identifies_active(self):
        result = detect_voice(self.analyze("membuka"))
        self.assertEqual(result["voice"], "active")

    def test_meng_prefix_identifies_active(self):
        result = detect_voice(self.analyze("mengambil"))
        self.assertEqual(result["voice"], "active")

    def test_ter_prefix_is_not_forced_to_passive(self):
        result = detect_voice(self.analyze("terima"))
        self.assertEqual(result["status"], "unresolved")
        self.assertIsNone(result["voice"])

    def test_ber_prefix_is_not_forced_to_active(self):
        result = detect_voice(self.analyze("berlari"))
        self.assertEqual(result["status"], "unresolved")

    def test_unknown_form_is_unresolved(self):
        result = detect_voice(self.analyze("xyzditulis"))
        self.assertEqual(result["status"], "unresolved")

    def test_non_verbal_candidate_is_ignored(self):
        nominal_lexicon = build_lexicon([entry("K1000", "tulis", ("NOUN",))])
        result = detect_voice(analyze_morphology("ditulis", nominal_lexicon))
        self.assertEqual(result["status"], "unresolved")

    def test_conflicting_voice_candidates_remain_ambiguous(self):
        active = self.analyze("menulis")[0]
        passive = self.analyze("ditulis")[0]
        result = detect_voice([active, passive])
        self.assertEqual(result["status"], "ambiguous")
        self.assertIsNone(result["voice"])

    def test_rejects_non_list(self):
        with self.assertRaises(TypeError):
            detect_voice(None)


if __name__ == "__main__":
    unittest.main()

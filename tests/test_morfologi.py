"""Regression tests for conservative Indonesian morphology."""
import unittest

from tools.morfologi import analyze_morphology
from tools.pencocokan_kamus import build_lexicon


def entry(entry_id, lemma):
    return {
        "id": entry_id,
        "lemma": lemma,
        "pos": ["VERB"],
        "senses": [{"sense_id": f"{entry_id}-S1", "definition": "Makna."}],
        "register": ["neutral"],
        "variants": [],
        "derived_forms": [],
    }


class MorphologyTests(unittest.TestCase):
    def setUp(self):
        self.lexicon = build_lexicon([
            entry("K0001", "makan"),
            entry("K0002", "ajar"),
            entry("K0003", "pukul"),
            entry("K0004", "tulis"),
            entry("K0005", "sapu"),
            entry("K0006", "lari"),
            entry("K0007", "anak"),
            entry("K0008", "main"),
        ])

    def bases(self, token):
        return {item["base_form"] for item in analyze_morphology(token, self.lexicon)}

    def test_suffix_an(self):
        self.assertIn("makan", self.bases("makanan"))

    def test_prefix_ber(self):
        self.assertIn("lari", self.bases("berlari"))

    def test_prefix_di(self):
        self.assertIn("tulis", self.bases("ditulis"))

    def test_nasal_restoration_mem(self):
        self.assertIn("pukul", self.bases("memukul"))

    def test_nasal_restoration_men(self):
        self.assertIn("tulis", self.bases("menulis"))

    def test_nasal_restoration_meny(self):
        self.assertIn("sapu", self.bases("menyapu"))

    def test_prefix_and_suffix_combination(self):
        self.assertIn("ajar", self.bases("mengajarkan"))

    def test_identical_reduplication(self):
        self.assertIn("anak", self.bases("anak-anak"))

    def test_non_identical_reduplication_not_guessed(self):
        self.assertEqual(self.bases("sayur-mayur"), set())

    def test_exact_lexical_match_is_not_stemmed(self):
        self.assertEqual(analyze_morphology("makan", self.lexicon), [])

    def test_unknown_form_is_not_forced(self):
        self.assertEqual(analyze_morphology("memperindah", self.lexicon), [])

    def test_rejects_non_string(self):
        with self.assertRaises(TypeError):
            analyze_morphology(None, self.lexicon)


if __name__ == "__main__":
    unittest.main()

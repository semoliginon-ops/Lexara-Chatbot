"""Regression tests for conservative Indonesian morphology."""
import unittest
from tools.morfologi import analyze_morphology
from tools.pencocokan_kamus import build_lexicon


def entry(entry_id, lemma):
    return {
        "id": entry_id, "lemma": lemma, "pos": ["VERB"],
        "senses": [{"sense_id": f"{entry_id}-S1", "definition": "Makna."}],
        "register": ["neutral"], "variants": [], "derived_forms": [],
    }


class MorphologyTests(unittest.TestCase):
    def setUp(self):
        lemmas = [
            "makan", "ajar", "pukul", "tulis", "sapu", "lari", "anak",
            "main", "indah", "baik", "bangun", "cat", "kerja", "anda", "mari",
            "ong", "lalu", "lati", "lapa", "ang", "api", "reka", "gecat",
        ]
        self.lexicon = build_lexicon([
            entry(f"K{i:04d}", lemma) for i, lemma in enumerate(lemmas, 1)
        ])

    def bases(self, token):
        return {item["base_form"] for item in analyze_morphology(token, self.lexicon)}

    def test_suffix_an(self): self.assertIn("makan", self.bases("makanan"))
    def test_prefix_ber(self): self.assertIn("lari", self.bases("berlari"))
    def test_prefix_di(self): self.assertIn("tulis", self.bases("ditulis"))
    def test_nasal_restoration_mem(self): self.assertIn("pukul", self.bases("memukul"))
    def test_nasal_restoration_men(self): self.assertIn("tulis", self.bases("menulis"))
    def test_nasal_restoration_meny(self): self.assertIn("sapu", self.bases("menyapu"))
    def test_prefix_and_suffix_combination(self): self.assertIn("ajar", self.bases("mengajarkan"))
    def test_identical_reduplication(self): self.assertIn("anak", self.bases("anak-anak"))
    def test_non_identical_reduplication_not_guessed(self): self.assertEqual(self.bases("sayur-mayur"), set())
    def test_exact_lexical_match_is_not_stemmed(self): self.assertEqual(analyze_morphology("makan", self.lexicon), [])
    def test_unknown_form_is_not_forced(self): self.assertEqual(analyze_morphology("memperxyz", self.lexicon), [])
    def test_prefix_memper(self): self.assertIn("indah", self.bases("memperindah"))
    def test_confix_ke_an(self): self.assertIn("indah", self.bases("keindahan"))
    def test_confix_ke_an_second_example(self): self.assertIn("baik", self.bases("kebaikan"))
    def test_confix_per_an(self): self.assertIn("main", self.bases("permainan"))
    def test_confix_peN_an_nasal_p(self): self.assertIn("bangun", self.bases("pembangunan"))
    def test_confix_peN_an_nasal_k(self): self.assertIn("ajar", self.bases("pengajaran"))
    def test_prefix_menge(self): self.assertIn("cat", self.bases("mengecat"))
    def test_lexicalized_beranda_not_split(self): self.assertNotIn("anda", self.bases("beranda"))
    def test_lexicalized_kemari_not_split(self): self.assertNotIn("mari", self.bases("kemari"))
    def test_lexicalized_terong_not_split(self): self.assertNotIn("ong", self.bases("terong"))
    def test_lexicalized_selalu_not_split(self): self.assertNotIn("lalu", self.bases("selalu"))
    def test_lexicalized_melati_not_split(self): self.assertNotIn("lati", self.bases("melati"))
    def test_lexicalized_kelapa_not_split(self): self.assertNotIn("lapa", self.bases("kelapa"))
    def test_lexicalized_perang_not_split(self): self.assertNotIn("ang", self.bases("perang"))
    def test_lexicalized_terapi_not_split(self): self.assertNotIn("api", self.bases("terapi"))
    def test_lexicalized_mereka_not_split(self): self.assertNotIn("reka", self.bases("mereka"))
    def test_penge_prefix_does_not_create_shorter_pen_candidate(self):
        bases = self.bases("pengecatan")
        self.assertIn("cat", bases)
        self.assertNotIn("gecat", bases)

    def test_ambiguous_base_keeps_all_pos_and_senses(self):
        ambiguous = {
            "id": "K9000",
            "lemma": "bisa",
            "pos": ["VERB", "NOUN"],
            "senses": [
                {"sense_id": "K9000-S1", "definition": "Mampu."},
                {"sense_id": "K9000-S2", "definition": "Racun."},
            ],
            "register": ["neutral"],
            "variants": [],
            "derived_forms": [],
        }
        lexicon = build_lexicon([ambiguous])
        results = analyze_morphology("membisa", lexicon)
        self.assertEqual(len(results), 1)
        candidate = results[0]["candidates"][0]["entry"]
        self.assertEqual(candidate["pos"], ["VERB", "NOUN"])
        self.assertEqual(len(candidate["senses"]), 2)

    def test_rejects_non_string(self):
        with self.assertRaises(TypeError): analyze_morphology(None, self.lexicon)


if __name__ == "__main__":
    unittest.main()

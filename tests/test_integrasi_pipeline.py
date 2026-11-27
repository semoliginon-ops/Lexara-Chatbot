"""End-to-end integration tests using the real 3,000-lemma dictionary."""
from pathlib import Path
import unittest

from tools.analisis_teks import analyze_text
from tools.kamus_loader import load_dictionary_directory
from tools.pencocokan_kamus import build_lexicon
from tools.pos_context import disambiguate_pos_context
from tools.pos_tagger import tag_pos


ROOT = Path(__file__).resolve().parents[1]


class FullDictionaryPipelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.entries = load_dictionary_directory(ROOT / "data" / "kamus")
        cls.lexicon = build_lexicon(cls.entries)

    def analyze(self, text):
        lexical = analyze_text(text, self.lexicon)
        tagged = tag_pos(lexical)
        return disambiguate_pos_context(tagged)

    @staticmethod
    def token(result, surface):
        return next(item for item in result["tokens"] if item["token"] == surface)

    def test_loads_full_dictionary_without_duplicate_lemmas(self):
        self.assertEqual(len(self.entries), 3000)
        self.assertGreater(len(self.lexicon), 3000)
        self.assertIn("aku", self.lexicon)
        self.assertIn("rumah", self.lexicon)

    def test_explicit_derived_form_pos_survives_full_pipeline(self):
        expected = {
            "bekerja": ("kerja", "VERB"),
            "menjelaskan": ("jelas", "VERB"),
            "letakkan": ("letak", "VERB"),
        }
        for surface, (lemma, pos) in expected.items():
            with self.subTest(surface=surface):
                result = self.analyze(surface)
                item = self.token(result, surface)
                self.assertEqual(item["status"], "matched")
                self.assertEqual(item["pos"], [pos])
                self.assertEqual(item["pos_source"], "dictionary")
                self.assertEqual(item["pos_status"], "identified")
                self.assertTrue(
                    any(candidate["lemma"] == lemma for candidate in item["candidates"])
                )

    def test_context_resolves_real_dictionary_ambiguity_conservatively(self):
        verb_result = self.analyze("sedang jalan")
        verb = self.token(verb_result, "jalan")
        self.assertEqual(verb["pos"], ["NOUN", "VERB"])
        self.assertEqual(verb["context_pos"], "VERB")
        self.assertEqual(verb["pos_context_status"], "selected_by_context")

        noun_result = self.analyze("di jalan")
        noun = self.token(noun_result, "jalan")
        self.assertEqual(noun["pos"], ["NOUN", "VERB"])
        self.assertEqual(noun["context_pos"], "NOUN")
        self.assertEqual(noun["pos_context_status"], "selected_by_context")

    def test_ambiguity_is_not_forced_without_context(self):
        item = self.token(self.analyze("jalan"), "jalan")
        self.assertEqual(item["pos"], ["NOUN", "VERB"])
        self.assertIsNone(item["context_pos"])
        self.assertEqual(item["pos_context_status"], "ambiguous")

    def test_normalization_unknown_words_and_punctuation_flow_end_to_end(self):
        result = self.analyze("  AKU   bekerja! ")
        self.assertEqual(result["normalized_text"], "aku bekerja!")
        self.assertEqual(
            [item["token"] for item in result["tokens"]],
            ["aku", "bekerja", "!"],
        )
        self.assertEqual(self.token(result, "aku")["pos"], ["PRON"])
        self.assertEqual(self.token(result, "bekerja")["pos"], ["VERB"])
        punctuation = self.token(result, "!")
        self.assertEqual(punctuation["kind"], "punctuation")
        self.assertEqual(punctuation["pos_status"], "not_applicable")


if __name__ == "__main__":
    unittest.main()

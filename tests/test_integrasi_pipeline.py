"""End-to-end integration tests using the real 3,000-lemma dictionary."""
from pathlib import Path
import unittest

from tools.analisis_teks import analyze_text
from tools.kamus_loader import load_dictionary_directory
from tools.pencocokan_kamus import build_lexicon
from tools.pos_context import disambiguate_pos_context
from tools.pos_tagger import tag_pos
from tools.parser_kalimat import parse_sentence


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

    def test_simple_sentence_parser_uses_real_dictionary_pipeline(self):
        result = self.analyze("Aku sedang bekerja di rumah.")
        parsed = parse_sentence(result)
        self.assertEqual(parsed["status"], "parsed")
        self.assertEqual(parsed["pattern"], "S-P-K")
        self.assertEqual(parsed["roles"]["subject"], ["aku"])
        self.assertEqual(parsed["roles"]["predicate"], ["sedang", "bekerja"])
        self.assertEqual(
            parsed["roles"]["adjuncts"],
            [{"preposition": "di", "phrase": ["rumah"]}],
        )

    def test_fronted_prepositional_adjunct_uses_real_dictionary_pipeline(self):
        result = parse_sentence(self.analyze("Di rumah aku bekerja."))
        self.assertEqual(result["status"], "parsed")
        self.assertEqual(result["pattern"], "S-P-K")
        self.assertEqual(result["roles"]["subject"], ["aku"])
        self.assertEqual(result["roles"]["predicate"], ["bekerja"])
        self.assertEqual(
            result["roles"]["adjuncts"],
            [{"preposition": "di", "phrase": ["rumah"]}],
        )

    def test_verbal_negation_parses_through_real_dictionary_pipeline(self):
        result = parse_sentence(self.analyze("Kami tidak membeli ikan."))
        self.assertEqual(result["status"], "parsed")
        self.assertEqual(result["pattern"], "S-P-O")
        self.assertEqual(result["roles"]["subject"], ["kami"])
        self.assertEqual(result["roles"]["predicate"], ["tidak", "membeli"])
        self.assertEqual(result["roles"]["object"], ["ikan"])


    def test_adjectival_nonverbal_predicate_uses_real_dictionary_pipeline(self):
        result = parse_sentence(self.analyze("Dia sakit."))
        self.assertEqual(result["status"], "parsed")
        self.assertEqual(result["pattern"], "S-P")
        self.assertEqual(result["roles"]["subject"], ["Dia".lower()])
        self.assertEqual(result["roles"]["predicate"], ["sakit"])

    def test_demonstrative_subject_nonverbal_predicate_uses_real_pipeline(self):
        result = self.analyze("Rumah itu besar.")
        self.assertEqual(self.token(result, "rumah")["pos"], ["NOUN"])
        self.assertEqual(self.token(result, "itu")["pos"], ["PRON"])
        self.assertEqual(self.token(result, "besar")["pos"], ["ADJ"])
        parsed = parse_sentence(result)
        self.assertEqual(parsed["status"], "parsed")
        self.assertEqual(parsed["pattern"], "S-P")
        self.assertEqual(parsed["roles"]["subject"], ["rumah", "itu"])
        self.assertEqual(parsed["roles"]["predicate"], ["besar"])

    def test_uncovered_linking_verb_becomes_unknown_and_parser_abstains(self):
        result = self.analyze("Dia menjadi dokter.")
        verb = self.token(result, "menjadi")
        self.assertEqual(verb["status"], "unknown")
        self.assertEqual(verb["pos"], [])
        parsed = parse_sentence(result)
        self.assertEqual(parsed["status"], "unresolved")
        self.assertEqual(parsed["roles"]["complement"], [])

    def test_uncovered_adjectival_complement_is_not_guessed(self):
        result = self.analyze("Mereka tampak bahagia.")
        linking_verb = self.token(result, "tampak")
        adjective = self.token(result, "bahagia")
        self.assertEqual(linking_verb["status"], "matched")
        self.assertEqual(linking_verb["pos"], ["VERB"])
        self.assertEqual(linking_verb["pos_source"], "dictionary")
        self.assertEqual(adjective["status"], "unknown")
        parsed = parse_sentence(result)
        self.assertEqual(parsed["status"], "partial")
        self.assertEqual(parsed["roles"]["predicate"], ["tampak"])
        self.assertEqual(parsed["roles"]["complement"], [])
        self.assertEqual(parsed["unresolved_tokens"], ["bahagia"])

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

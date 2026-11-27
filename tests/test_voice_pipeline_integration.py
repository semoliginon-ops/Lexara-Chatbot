"""End-to-end checks from morphology evidence to parser predicate voice."""
import unittest

from tools.analisis_teks import analyze_text
from tools.hubungkan_voice_predikat import connect_predicate_voice
from tools.parser_kalimat import parse_sentence
from tools.pencocokan_kamus import build_lexicon


def entry(entry_id, lemma):
    return {
        "id": entry_id,
        "lemma": lemma,
        "pos": ["VERB"],
        "senses": [{"sense_id": f"{entry_id}-S1", "definition": "Makna uji."}],
        "register": ["neutral"],
        "variants": [],
        "derived_forms": [],
    }


def parser_token(value, pos):
    return {
        "token": value,
        "kind": "word",
        "pos": [pos],
        "pos_status": "identified",
        "context_pos": None,
        "pos_context_status": None,
    }


class VoicePipelineIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.lexicon = build_lexicon([
            entry("K9001", "tulis"),
            entry("K9002", "buka"),
        ])

    def test_real_active_morphology_connects_to_parser_predicate_head(self):
        analyzed = analyze_text("Rina menulis surat.", self.lexicon)
        parsed = parse_sentence({"tokens": [
            parser_token("Rina", "NOUN"),
            parser_token("menulis", "VERB"),
            parser_token("surat", "NOUN"),
            {
                "token": ".",
                "kind": "punctuation",
                "pos": [],
                "pos_status": "not_applicable",
            },
        ]})
        self.assertEqual(parsed["status"], "parsed")
        result = connect_predicate_voice(parsed, analyzed)
        self.assertEqual(result["status"], "identified")
        self.assertEqual(result["voice"], "active")
        self.assertEqual(result["predicate_head"], "menulis")

    def test_real_passive_morphology_connects_to_parser_predicate_head(self):
        analyzed = analyze_text("Surat ditulis Rina.", self.lexicon)
        parsed = parse_sentence({"tokens": [
            parser_token("Surat", "NOUN"),
            parser_token("ditulis", "VERB"),
            parser_token("Rina", "NOUN"),
            {
                "token": ".",
                "kind": "punctuation",
                "pos": [],
                "pos_status": "not_applicable",
            },
        ]})
        self.assertEqual(parsed["status"], "parsed")
        result = connect_predicate_voice(parsed, analyzed)
        self.assertEqual(result["status"], "identified")
        self.assertEqual(result["voice"], "passive")
        self.assertEqual(result["predicate_head"], "ditulis")

    def test_ter_form_remains_unresolved_through_pipeline(self):
        analyzed = analyze_text("Pintu terbuka.", self.lexicon)
        parsed = parse_sentence({"tokens": [
            parser_token("Pintu", "NOUN"),
            parser_token("terbuka", "VERB"),
            {
                "token": ".",
                "kind": "punctuation",
                "pos": [],
                "pos_status": "not_applicable",
            },
        ]})
        self.assertEqual(parsed["status"], "parsed")
        result = connect_predicate_voice(parsed, analyzed)
        self.assertEqual(result["status"], "unresolved")
        self.assertEqual(result["reason"], "no_confirmed_voice_morphology")


if __name__ == "__main__":
    unittest.main()

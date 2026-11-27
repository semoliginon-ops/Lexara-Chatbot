"""End-to-end checks from morphology evidence to parser predicate voice."""
import unittest
from pathlib import Path

from tools.kamus_loader import load_batch
from tools.pemetaan_peran_semantis import map_semantic_roles
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
        root = Path(__file__).resolve().parents[1]
        entries = load_batch(root / "data" / "kamus" / "batch-002.jsonl")
        cls.buka_sense = next(item for item in entries if item["id"] == "K0065")["senses"][0]

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

    def test_confirmed_passive_voice_flows_into_semantic_role_mapping(self):
        analyzed = analyze_text("Pintu dibuka oleh Rina.", self.lexicon)
        parsed = parse_sentence({"tokens": [
            parser_token("Pintu", "NOUN"),
            parser_token("dibuka", "VERB"),
            parser_token("oleh", "PREP"),
            parser_token("Rina", "NOUN"),
            {
                "token": ".",
                "kind": "punctuation",
                "pos": [],
                "pos_status": "not_applicable",
            },
        ]})
        self.assertEqual(parsed["status"], "parsed")
        voice = connect_predicate_voice(parsed, analyzed)
        self.assertEqual(voice["status"], "identified")
        self.assertEqual(voice["voice"], "passive")
        mapped = map_semantic_roles(parsed, self.buka_sense, voice=voice["voice"])
        self.assertEqual(mapped["status"], "ambiguous")
        self.assertTrue(all(
            frame["arguments"][1]["semantic_role"] == "PATIENT"
            and frame["arguments"][1]["value"] == ["Pintu"]
            for frame in mapped["candidates"]
        ))
    def test_postverbal_agent_passive_flows_through_full_pipeline(self):
        analyzed = analyze_text("Pintu dibuka Rina.", self.lexicon)
        parsed = parse_sentence({"tokens": [
            parser_token("Pintu", "NOUN"),
            parser_token("dibuka", "VERB"),
            parser_token("Rina", "NOUN"),
            {"token": ".", "kind": "punctuation", "pos": [], "pos_status": "not_applicable"},
        ]})
        voice = connect_predicate_voice(parsed, analyzed)
        self.assertEqual(voice["voice"], "passive")
        mapped = map_semantic_roles(parsed, self.buka_sense, voice=voice["voice"])
        self.assertEqual(mapped["status"], "ambiguous")
        for frame in mapped["candidates"]:
            self.assertEqual(frame["arguments"][0]["value"], ["Rina"])
            self.assertEqual(frame["arguments"][0]["realization"], "postverbal_agent")
            self.assertEqual(frame["arguments"][1]["value"], ["Pintu"])

    def test_agentless_passive_flows_through_full_pipeline(self):
        analyzed = analyze_text("Pintu dibuka.", self.lexicon)
        parsed = parse_sentence({"tokens": [
            parser_token("Pintu", "NOUN"),
            parser_token("dibuka", "VERB"),
            {"token": ".", "kind": "punctuation", "pos": [], "pos_status": "not_applicable"},
        ]})
        voice = connect_predicate_voice(parsed, analyzed)
        self.assertEqual(voice["voice"], "passive")
        mapped = map_semantic_roles(parsed, self.buka_sense, voice=voice["voice"])
        self.assertEqual(mapped["status"], "ambiguous")
        for frame in mapped["candidates"]:
            self.assertEqual(frame["arguments"][0]["presence"], "omitted")
            self.assertEqual(frame["arguments"][1]["value"], ["Pintu"])
    def test_active_and_passive_voice_preserve_agent_causer_alternatives(self):
        active_analysis = analyze_text("Angin membuka pintu.", self.lexicon)
        active_parse = parse_sentence({"tokens": [
            parser_token("Angin", "NOUN"),
            parser_token("membuka", "VERB"),
            parser_token("pintu", "NOUN"),
            {"token": ".", "kind": "punctuation", "pos": [], "pos_status": "not_applicable"},
        ]})
        active_voice = connect_predicate_voice(active_parse, active_analysis)
        self.assertEqual(active_voice["voice"], "active")
        active_map = map_semantic_roles(active_parse, self.buka_sense, voice=active_voice["voice"])
        self.assertEqual(active_map["status"], "ambiguous")

        passive_analysis = analyze_text("Pintu dibuka angin.", self.lexicon)
        passive_parse = parse_sentence({"tokens": [
            parser_token("Pintu", "NOUN"),
            parser_token("dibuka", "VERB"),
            parser_token("angin", "NOUN"),
            {"token": ".", "kind": "punctuation", "pos": [], "pos_status": "not_applicable"},
        ]})
        passive_voice = connect_predicate_voice(passive_parse, passive_analysis)
        self.assertEqual(passive_voice["voice"], "passive")
        passive_map = map_semantic_roles(passive_parse, self.buka_sense, voice=passive_voice["voice"])
        self.assertEqual(passive_map["status"], "ambiguous")
        for mapped in (active_map, passive_map):
            subject_roles = {
                next(a["semantic_role"] for a in frame["arguments"] if a["syntactic_role"] == "SUBJ")
                for frame in mapped["candidates"]
            }
            self.assertEqual(subject_roles, {"AGENT", "CAUSER"})
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

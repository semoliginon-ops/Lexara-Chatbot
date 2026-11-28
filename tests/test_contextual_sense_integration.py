import json
import tempfile
import unittest
from pathlib import Path

from tools.analisis_teks import analyze_text
from tools.kamus_loader import load_dictionary_directory
from tools.pencocokan_kamus import build_lexicon
from tools.pos_context import disambiguate_pos_context
from tools.pos_tagger import tag_pos
from tools.parser_kalimat import parse_sentence

from tools.context_rules_loader import load_context_rules, ContextRulesLoadError
from tools.contextual_sense_integration import orchestrate_contextual_senses


def concept_layer():
    return {
        "concepts": [
            {"concept_id": "C000001", "label": "makna satu", "definition": "definisi", "status": "reviewed"},
            {"concept_id": "C000002", "label": "makna dua", "definition": "definisi", "status": "reviewed"},
        ],
        "mappings": [
            {"sense_id": "S1", "concept_id": "C000001", "status": "reviewed"},
            {"sense_id": "S2", "concept_id": "C000002", "status": "reviewed"},
        ],
        "relations": [],
    }


def lexical_candidate(sense_ids):
    return [{
        "entry_id": "E1",
        "lemma": "kata",
        "matched_form": "kata",
        "match_type": "lemma",
        "entry": {
            "id": "E1",
            "lemma": "kata",
            "pos": ["NOUN"],
            "senses": [{"sense_id": sense_id, "definition": "definisi " + sense_id} for sense_id in sense_ids],
        },
    }]


def analysis(*items):
    return {"tokens": [
        {"token": token, "kind": "word", "candidates": candidates}
        for token, candidates in items
    ]}


def rule(rule_id, sense_id, polarity="supports", status="reviewed", cue="besok"):
    return {
        "rule_id": rule_id,
        "status": status,
        "target_sense_id": sense_id,
        "conditions": [
            {"type": "token_present", "value": cue},
            {"type": "role_contains", "role": "adjuncts", "value": cue},
        ],
        "polarity": polarity,
        "strength": "strong",
        "source": "fixture",
        "rationale": "aturan fixture yang eksplisit",
    }


class ContextualSenseIntegrationTests(unittest.TestCase):
    def test_selects_one_sense_from_strong_support_and_alternative_contradiction(self):
        result = orchestrate_contextual_senses(
            analysis(("kata", lexical_candidate(["S1", "S2"]))),
            {"status": "parsed", "roles": {"subject": ["kata"], "predicate": [], "object": [], "adjuncts": [{"preposition": "pada", "phrase": ["besok"]}], "complement": []}, "unresolved_tokens": []},
            concept_layer(),
            [rule("CE000001", "S1", "supports"), rule("CE000002", "S2", "contradicts")],
        )
        self.assertEqual(result["results"][0]["selection"]["status"], "selected")
        self.assertEqual(result["results"][0]["selection"]["selected_sense_id"], "S1")

    def test_each_token_occurrence_gets_its_own_candidate_group_and_evidence(self):
        result = orchestrate_contextual_senses(
            analysis(("kata", lexical_candidate(["S1"])), ("lain", lexical_candidate(["S2"]))),
            {"status": "parsed", "roles": {"subject": ["kata"], "predicate": ["lain"], "object": [], "adjuncts": [{"adverb": "besok", "kind": "temporal"}], "complement": []}, "unresolved_tokens": []},
            concept_layer(),
            [rule("CE000001", "S1"), rule("CE000002", "S2")],
        )
        self.assertEqual(len(result["results"]), 2)
        self.assertEqual([item["token_index"] for item in result["results"]], [0, 1])
        self.assertEqual([item["evidence"][0]["sense_id"] for item in result["results"]], ["S1", "S2"])

    def test_repeated_surface_form_is_deferred(self):
        result = orchestrate_contextual_senses(
            analysis(("kata", lexical_candidate(["S1"])), ("kata", lexical_candidate(["S1"]))),
            {"status": "parsed", "roles": {"subject": ["kata"], "predicate": ["kata"], "object": [], "adjuncts": [], "complement": []}, "unresolved_tokens": []},
            concept_layer(), [],
        )
        self.assertEqual([item["defer_reason"] for item in result["results"]], [
            "repeated_surface_form_mapping_ambiguous",
            "repeated_surface_form_mapping_ambiguous",
        ])

    def test_compound_clause_result_is_deferred(self):
        result = orchestrate_contextual_senses(
            analysis(("kata", lexical_candidate(["S1"]))),
            {"status": "parsed", "clauses": [{"analysis": {"status": "parsed"}}], "roles": {"subject": [], "predicate": [], "object": [], "adjuncts": [], "complement": []}, "unresolved_tokens": []},
            concept_layer(), [],
        )
        self.assertEqual(result["results"][0]["defer_reason"], "compound_clause_context_deferred")
        unresolved = orchestrate_contextual_senses(
            analysis(("kata", lexical_candidate(["S1"]))),
            {"status": "unresolved", "roles": {"subject": [], "predicate": ["kata"], "object": [], "adjuncts": [], "complement": []}, "unresolved_tokens": []},
            concept_layer(), [],
        )
        self.assertEqual(unresolved["results"][0]["defer_reason"], "parser_status_not_usable")

    def test_partial_parser_uses_available_confirmed_observations(self):
        result = orchestrate_contextual_senses(
            analysis(("kata", lexical_candidate(["S1"]))),
            {"status": "partial", "roles": {"subject": ["kata"], "predicate": [], "object": [], "adjuncts": [{"adverb": "besok", "kind": "temporal"}], "complement": []}, "unresolved_tokens": ["entitas"]},
            concept_layer(), [rule("CE000001", "S1")],
        )
        self.assertEqual(result["results"][0]["orchestration_status"], "processed")
        self.assertEqual(result["results"][0]["evidence_status"], "evidence_found")

    def test_partial_parser_target_token_unresolved_is_deferred(self):
        result = orchestrate_contextual_senses(
            analysis(("kata", lexical_candidate(["S1"]))),
            {"status": "partial", "roles": {"subject": [], "predicate": [], "object": [], "adjuncts": [{"adverb": "besok", "kind": "temporal"}], "complement": []}, "unresolved_tokens": ["kata"]},
            concept_layer(), [rule("CE000001", "S1")],
        )
        self.assertEqual(result["results"][0]["defer_reason"], "target_token_unresolved_by_parser")

    def test_non_reviewed_rule_does_not_generate_evidence(self):
        result = orchestrate_contextual_senses(
            analysis(("kata", lexical_candidate(["S1"]))),
            {"status": "parsed", "roles": {"subject": ["kata"], "predicate": [], "object": [], "adjuncts": [{"adverb": "besok", "kind": "temporal"}], "complement": []}, "unresolved_tokens": []},
            concept_layer(), [rule("CE000001", "S1", status="proposed")],
        )
        self.assertEqual(result["results"][0]["evidence"], [])
        self.assertEqual(result["results"][0]["selection"]["status"], "not_needed")

    def test_unmapped_sense_is_preserved_without_inferred_concept(self):
        layer = concept_layer()
        layer["mappings"] = []
        result = orchestrate_contextual_senses(
            analysis(("kata", lexical_candidate(["S1"]))),
            {"status": "parsed", "roles": {"subject": ["kata"], "predicate": [], "object": [], "adjuncts": [], "complement": []}, "unresolved_tokens": []},
            layer, [],
        )
        item = result["results"][0]
        self.assertEqual(item["candidate_senses"][0]["mapping_status"], "unmapped")
        self.assertEqual(item["candidate_senses"][0]["concepts"], [])
        self.assertEqual(item["selection"]["status"], "not_needed")

    def test_inputs_are_not_mutated_and_output_is_deterministic(self):
        source = analysis(("kata", lexical_candidate(["S1"])))
        parsed = {"status": "parsed", "roles": {"subject": ["kata"], "predicate": [], "object": [], "adjuncts": [], "complement": []}, "unresolved_tokens": []}
        layer = concept_layer()
        rules = []
        before = json.dumps([source, parsed, layer, rules], sort_keys=True)
        first = orchestrate_contextual_senses(source, parsed, layer, rules)
        second = orchestrate_contextual_senses(source, parsed, layer, rules)
        self.assertEqual(first, second)
        self.assertEqual(json.dumps([source, parsed, layer, rules], sort_keys=True), before)

        root = Path(__file__).resolve().parents[1]
        entries = load_dictionary_directory(root / "data" / "kamus")
        lexicon = build_lexicon(entries)
        lexical = analyze_text("Aku makan nasi besok.", lexicon)
        tagged = disambiguate_pos_context(tag_pos(lexical))
        parsed_sentence = parse_sentence(tagged)
        integrated = orchestrate_contextual_senses(
            tagged, parsed_sentence, concept_layer(), []
        )
        self.assertEqual(parsed_sentence["status"], "parsed")
        self.assertEqual(integrated["status"], "completed")
        self.assertEqual(
            [item["token"] for item in integrated["results"] if item["orchestration_status"] == "processed"],
            ["aku", "makan", "nasi", "besok"],
        )

    def test_context_rules_loader_reads_jsonl_and_rejects_invalid_rows(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "rules.jsonl"
            expected = [rule("CE000001", "S1")]
            path.write_text(json.dumps(expected[0]) + "\n", encoding="utf-8")
            self.assertEqual(load_context_rules(path), expected)
            path.write_text("", encoding="utf-8")
            self.assertEqual(load_context_rules(path), [])
            path.write_text("{broken}\n", encoding="utf-8")
            with self.assertRaises(ContextRulesLoadError):
                load_context_rules(path)


if __name__ == "__main__":
    unittest.main()

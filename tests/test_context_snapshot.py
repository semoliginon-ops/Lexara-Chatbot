import json
import unittest

from tools.context_snapshot import build_context_snapshot, ContextSnapshotError


def token(text, **extra):
    value = {
        "token": text,
        "kind": "word",
        "status": "matched",
        "candidates": [{"lemma": text, "sense_ids": ["K0001-S1"]}],
        "morphology_candidates": [{"base_form": text, "rule": "lemma"}],
        "voice_analysis": {"status": "unresolved", "label": None},
        "pos_candidates": [{"pos": ["NOUN"]}],
        "pos": ["NOUN"],
        "pos_status": "identified",
        "context_pos": "NOUN",
        "pos_context_status": "unambiguous",
        "pos_context_evidence": [],
    }
    value.update(extra)
    return value


def parsed(roles=None, status="parsed", unresolved=None, **extra):
    result = {
        "parser_method": "fixture_parser",
        "status": status,
        "pattern": "S-P",
        "roles": roles or {
            "subject": [], "predicate": [], "object": [],
            "adjuncts": [], "complement": [],
        },
        "unresolved_tokens": unresolved or [],
        "notes": [],
    }
    result.update(extra)
    return result


class ContextSnapshotTests(unittest.TestCase):
    def test_combines_lexical_morphology_voice_and_pos_without_losing_candidates(self):
        source = {"normalized_text": "kata", "tokens": [token(
            "kata",
            candidates=[{"lemma": "kata", "sense_ids": ["S1", "S2"]}],
            morphology_candidates=[{"base_form": "kata", "rule": "prefix"}],
            voice_analysis={"status": "identified", "label": "active"},
            pos_candidates=[{"pos": ["NOUN", "VERB"]}],
            pos=["NOUN", "VERB"],
            context_pos="VERB",
            pos_context_status="selected_by_context",
            pos_context_evidence=[{"rule": "fixture", "pos": "VERB"}],
        )]}
        result = build_context_snapshot(
            source,
            parsed({"subject": [], "predicate": ["kata"], "object": [], "adjuncts": [], "complement": []}),
        )
        item = result["tokens"][0]
        self.assertEqual(item["lexical_candidates"][0]["sense_ids"], ["S1", "S2"])
        self.assertEqual(item["morphology_candidates"][0]["rule"], "prefix")
        self.assertEqual(item["voice_analysis"]["label"], "active")
        self.assertEqual(item["pos"], ["NOUN", "VERB"])
        self.assertEqual(item["context_pos"], "VERB")
        self.assertEqual(item["syntactic_role"], "predicate")

    def test_preserves_token_order_and_occurrence_indices(self):
        source = {"tokens": [token("aku"), token("makan"), token("nasi")]}
        result = build_context_snapshot(
            source,
            parsed({"subject": ["aku"], "predicate": ["makan"], "object": ["nasi"], "adjuncts": [], "complement": []}),
        )
        self.assertEqual([item["token_index"] for item in result["tokens"]], [0, 1, 2])
        self.assertEqual([item["token"] for item in result["tokens"]], ["aku", "makan", "nasi"])
        self.assertEqual([item["syntactic_role"] for item in result["tokens"]], ["subject", "predicate", "object"])

    def test_maps_subject_predicate_object_and_complement_roles(self):
        source = {"tokens": [token("dia"), token("menjadi"), token("dokter"), token("hebat")]}
        result = build_context_snapshot(
            source,
            parsed({"subject": ["dia"], "predicate": ["menjadi"], "object": [], "adjuncts": [], "complement": ["dokter", "hebat"]}),
        )
        self.assertEqual(
            [item["syntactic_role"] for item in result["tokens"]],
            ["subject", "predicate", "complement", "complement"],
        )

    def test_maps_adjunct_tokens_from_supported_nested_parser_shape(self):
        source = {"tokens": [token("besok"), token("di"), token("rumah")]}
        result = build_context_snapshot(
            source,
            parsed({"subject": [], "predicate": [], "object": [], "adjuncts": [
                {"adverb": "besok", "kind": "temporal"},
                {"preposition": "di", "phrase": ["rumah"]},
            ], "complement": []}),
        )
        self.assertEqual([item["syntactic_role"] for item in result["tokens"]], ["adjunct"] * 3)

    def test_punctuation_is_not_applicable(self):
        source = {"tokens": [token("aku"), {"token": ".", "kind": "punctuation", "status": "not_applicable", "candidates": []}]}
        result = build_context_snapshot(
            source,
            parsed({"subject": ["aku"], "predicate": [], "object": [], "adjuncts": [], "complement": []}),
        )
        self.assertEqual(result["tokens"][1]["syntax_status"], "not_applicable")
        self.assertIsNone(result["tokens"][1]["syntactic_role"])

    def test_parser_unresolved_token_is_not_assigned_a_role(self):
        source = {"tokens": [token("entitas")]}
        result = build_context_snapshot(
            source,
            parsed({"subject": [], "predicate": [], "object": [], "adjuncts": [], "complement": []}, status="partial", unresolved=["entitas"]),
        )
        item = result["tokens"][0]
        self.assertEqual(item["syntax_status"], "unresolved")
        self.assertIsNone(item["syntactic_role"])
        self.assertEqual(result["status"], "partial")

    def test_repeated_surface_form_is_deferred(self):
        source = {"tokens": [token("dia"), token("melihat"), token("dia")]}
        result = build_context_snapshot(
            source,
            parsed({"subject": ["dia"], "predicate": ["melihat"], "object": ["dia"], "adjuncts": [], "complement": []}),
        )
        repeated = [item for item in result["tokens"] if item["token"] == "dia"]
        self.assertEqual([item["syntax_status"] for item in repeated], ["deferred", "deferred"])
        self.assertEqual(result["status"], "deferred")

    def test_compound_clause_parser_result_defers_role_mapping(self):
        source = {"tokens": [token("aku"), token("pergi")]}
        result = build_context_snapshot(
            source,
            parsed({"subject": [], "predicate": [], "object": [], "adjuncts": [], "complement": []},
                   clauses=[{"analysis": {"roles": {"subject": ["aku"], "predicate": ["pergi"]}}}]),
        )
        self.assertEqual([item["syntax_status"] for item in result["tokens"]], ["deferred", "deferred"])
        self.assertEqual(result["status"], "deferred")
        self.assertIn("clauses", result["parser_result"])

    def test_partial_and_unobserved_tokens_are_preserved_without_negative_evidence(self):
        source = {"tokens": [token("aku"), token("mungkin"), token("pulang")]}
        result = build_context_snapshot(
            source,
            parsed({"subject": ["aku"], "predicate": [], "object": [], "adjuncts": [], "complement": []},
                   status="partial", unresolved=["pulang"]),
        )
        states = [item["syntax_status"] for item in result["tokens"]]
        self.assertEqual(states, ["mapped", "not_observed", "unresolved"])
        self.assertIsNone(result["tokens"][1]["syntactic_role"])
        self.assertEqual(result["status"], "partial")

    def test_inputs_are_unchanged_and_output_is_deterministic(self):
        source = {"normalized_text": "aku makan", "tokens": [token("aku"), token("makan")]}
        parser_result = parsed({"subject": ["aku"], "predicate": ["makan"], "object": [], "adjuncts": [], "complement": []})
        before = json.dumps([source, parser_result], sort_keys=True)
        first = build_context_snapshot(source, parser_result)
        second = build_context_snapshot(source, parser_result)
        self.assertEqual(first, second)
        self.assertEqual(json.dumps([source, parser_result], sort_keys=True), before)
        with self.assertRaises(ContextSnapshotError):
            build_context_snapshot({"tokens": "invalid"}, parsed())
        with self.assertRaises(ContextSnapshotError):
            build_context_snapshot({"tokens": [token("aku")]}, {"status": "parsed"})


if __name__ == "__main__":
    unittest.main()

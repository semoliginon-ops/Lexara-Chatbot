"""Tes terfokus untuk Context Evidence Generator v1."""
import copy
import unittest

from tools.context_evidence_generator import (
    ContextEvidenceGeneratorError,
    generate_context_evidence,
)


def candidate(sense_id="K0001-S1", concepts=None):
    return {
        "sense_id": sense_id,
        "concepts": (
            [{"concept_id": "C000001"}] if concepts is None else concepts
        ),
    }


def parse_result(status="parsed", roles=None, unresolved=None):
    return {
        "status": status,
        "roles": roles if roles is not None else {
            "subject": ["Aku"],
            "predicate": ["makan"],
            "object": ["nasi"],
            "adjuncts": [],
            "complement": [],
        },
        "unresolved_tokens": unresolved if unresolved is not None else [],
    }


def rule(
    rule_id="CE000001",
    status="reviewed",
    sense_id="K0001-S1",
    conditions=None,
    polarity="supports",
    strength="weak",
):
    return {
        "rule_id": rule_id,
        "status": status,
        "target_sense_id": sense_id,
        "conditions": conditions if conditions is not None else [
            {"type": "token_present", "value": "nasi"}
        ],
        "polarity": polarity,
        "strength": strength,
        "source": "anotasi-kurasi-001",
        "rationale": "Kondisi ini ditinjau untuk sense sasaran.",
    }


class ContextEvidenceGeneratorTests(unittest.TestCase):
    def test_parser_observations_without_reviewed_rules_are_not_evidence(self):
        result = generate_context_evidence(
            [candidate()],
            parse_result(),
            [],
        )
        self.assertEqual(result["observations"]["roles"]["object"], ["nasi"])
        self.assertEqual(result["evidence"], [])
        self.assertEqual(result["status"], "no_evidence")

    def test_reviewed_rule_emits_evidence_for_target_sense(self):
        result = generate_context_evidence(
            [candidate()],
            parse_result(),
            [rule()],
        )
        self.assertEqual(len(result["evidence"]), 1)
        evidence = result["evidence"][0]
        self.assertEqual(evidence["sense_id"], "K0001-S1")
        self.assertEqual(evidence["concept_ids"], ["C000001"])
        self.assertEqual(evidence["rule_id"], "CE000001")
        self.assertEqual(evidence["strength"], "weak")
        self.assertEqual(evidence["token_spans"], [])

    def test_proposed_and_rejected_rules_do_not_emit_evidence(self):
        rules = [
            rule("CE000001", status="proposed"),
            rule("CE000002", status="rejected"),
        ]
        result = generate_context_evidence([candidate()], parse_result(), rules)
        self.assertEqual(result["evidence"], [])
        self.assertEqual(result["status"], "no_evidence")

    def test_multiple_weak_rules_remain_separate_and_weak(self):
        rules = [
            rule("CE000001", conditions=[
                {"type": "token_present", "value": "nasi"}
            ]),
            rule("CE000002", conditions=[
                {"type": "role_contains", "role": "predicate", "value": "makan"}
            ]),
        ]
        result = generate_context_evidence([candidate()], parse_result(), rules)
        self.assertEqual(len(result["evidence"]), 2)
        self.assertEqual(
            [item["strength"] for item in result["evidence"]],
            ["weak", "weak"],
        )

    def test_strong_rule_requires_explicit_lexical_condition(self):
        invalid = rule(
            conditions=[
                {"type": "role_contains", "role": "object", "value": "nasi"}
            ],
            strength="strong",
        )
        with self.assertRaises(ContextEvidenceGeneratorError):
            generate_context_evidence([candidate()], parse_result(), [invalid])

        valid = rule(
            conditions=[
                {"type": "token_present", "value": "nasi"},
                {"type": "role_contains", "role": "object", "value": "nasi"},
            ],
            strength="strong",
        )
        result = generate_context_evidence([candidate()], parse_result(), [valid])
        self.assertEqual(result["evidence"][0]["strength"], "strong")

    def test_support_and_contradiction_are_both_preserved(self):
        rules = [
            rule("CE000001", polarity="supports"),
            rule("CE000002", polarity="contradicts"),
        ]
        result = generate_context_evidence([candidate()], parse_result(), rules)
        self.assertEqual(
            [item["polarity"] for item in result["evidence"]],
            ["supports", "contradicts"],
        )
        self.assertEqual(len(result["evidence"]), 2)

    def test_candidate_without_concept_mapping_can_receive_evidence(self):
        result = generate_context_evidence(
            [candidate(concepts=[])],
            parse_result(),
            [rule(strength="strong")],
        )
        self.assertEqual(result["evidence"][0]["sense_id"], "K0001-S1")
        self.assertEqual(result["evidence"][0]["concept_ids"], [])

    def test_partial_parser_uses_only_available_role_observations(self):
        partial = parse_result(
            status="partial",
            roles={"subject": ["Aku"], "predicate": ["makan"]},
            unresolved=["nasi"],
        )
        result = generate_context_evidence(
            [candidate()],
            partial,
            [rule(conditions=[
                {"type": "role_contains", "role": "object", "value": "nasi"}
            ])],
        )
        self.assertEqual(result["evidence"], [])
        self.assertEqual(result["observations"]["unresolved_tokens"], ["nasi"])
        self.assertEqual(result["status"], "no_evidence")

    def test_unresolved_parser_does_not_match_structural_conditions(self):
        unresolved = parse_result(
            status="unresolved",
            roles={"predicate": ["makan"]},
        )
        result = generate_context_evidence(
            [candidate()],
            unresolved,
            [rule(conditions=[
                {"type": "role_contains", "role": "predicate", "value": "makan"}
            ])],
        )
        self.assertEqual(result["evidence"], [])
        self.assertTrue(any("role" in note for note in result["notes"]))

    def test_inputs_are_unchanged_and_output_is_deterministic(self):
        candidates = [candidate()]
        parsed = parse_result()
        rules = [rule()]
        before = copy.deepcopy((candidates, parsed, rules))

        first = generate_context_evidence(candidates, parsed, rules)
        second = generate_context_evidence(candidates, parsed, rules)

        self.assertEqual((candidates, parsed, rules), before)
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()

"""Tests for evidence-gated contextual semantic-role resolution."""
import unittest

from tools.resolusi_peran_semantis import resolve_semantic_role_candidates


def ambiguous_result():
    return {
        "status": "ambiguous",
        "reason": "multiple_frames_match",
        "sense_id": "memecahkan-uji-S1",
        "candidates": [
            {
                "frame_id": "F_CAUSER",
                "arguments": [
                    {"argument_id": "A1", "syntactic_role": "SUBJ", "semantic_role": "CAUSER", "value": ["Palu"]},
                    {"argument_id": "A2", "syntactic_role": "OBJ", "semantic_role": "PATIENT", "value": ["Kaca"]},
                ],
            },
            {
                "frame_id": "F_INSTRUMENT",
                "arguments": [
                    {"argument_id": "A1", "syntactic_role": "SUBJ", "semantic_role": "INSTRUMENT", "value": ["Palu"]},
                    {"argument_id": "A2", "syntactic_role": "OBJ", "semantic_role": "PATIENT", "value": ["Kaca"]},
                ],
            },
        ],
    }


def evidence(frame_id, role, polarity, strength="strong"):
    return {
        "frame_id": frame_id,
        "argument_id": "A1",
        "semantic_role": role,
        "polarity": polarity,
        "strength": strength,
        "source": "controlled_context_annotation",
    }


class ContextualSemanticRoleResolutionTests(unittest.TestCase):
    def test_no_evidence_preserves_ambiguity(self):
        result = resolve_semantic_role_candidates(ambiguous_result())
        self.assertEqual(result["status"], "ambiguous")
        self.assertEqual(len(result["candidates"]), 2)
        self.assertEqual(result["context_resolution"]["status"], "unresolved")

    def test_support_without_excluding_alternative_is_not_enough(self):
        result = resolve_semantic_role_candidates(
            ambiguous_result(),
            [evidence("F_CAUSER", "CAUSER", "supports")],
        )
        self.assertEqual(result["status"], "ambiguous")
        self.assertEqual(result["context_resolution"]["reason"], "insufficient_discriminating_evidence")

    def test_resolves_only_when_one_supported_and_all_alternatives_excluded(self):
        result = resolve_semantic_role_candidates(
            ambiguous_result(),
            [
                evidence("F_CAUSER", "CAUSER", "supports"),
                evidence("F_INSTRUMENT", "INSTRUMENT", "contradicts"),
            ],
        )
        self.assertEqual(result["status"], "mapped")
        self.assertEqual([item["frame_id"] for item in result["candidates"]], ["F_CAUSER"])
        self.assertEqual(result["context_resolution"]["status"], "resolved")

    def test_weak_evidence_never_selects_a_frame(self):
        result = resolve_semantic_role_candidates(
            ambiguous_result(),
            [
                evidence("F_CAUSER", "CAUSER", "supports", "weak"),
                evidence("F_INSTRUMENT", "INSTRUMENT", "contradicts", "weak"),
            ],
        )
        self.assertEqual(result["status"], "ambiguous")
        self.assertEqual(len(result["context_resolution"]["ignored_evidence"]), 2)

    def test_conflicting_evidence_for_same_frame_abstains(self):
        result = resolve_semantic_role_candidates(
            ambiguous_result(),
            [
                evidence("F_CAUSER", "CAUSER", "supports"),
                evidence("F_CAUSER", "CAUSER", "contradicts"),
                evidence("F_INSTRUMENT", "INSTRUMENT", "contradicts"),
            ],
        )
        self.assertEqual(result["status"], "ambiguous")
        self.assertEqual(result["context_resolution"]["reason"], "conflicting_evidence")

    def test_unmatched_evidence_is_ignored(self):
        result = resolve_semantic_role_candidates(
            ambiguous_result(),
            [evidence("F_CAUSER", "INSTRUMENT", "supports")],
        )
        self.assertEqual(result["status"], "ambiguous")
        self.assertEqual(
            result["context_resolution"]["ignored_evidence"][0]["reason"],
            "argument_role_mismatch",
        )

    def test_invalid_evidence_is_rejected(self):
        with self.assertRaises(ValueError):
            resolve_semantic_role_candidates(ambiguous_result(), [{"frame_id": "F_CAUSER"}])

    def test_non_ambiguous_mapping_is_unchanged(self):
        mapping = {"status": "mapped", "candidates": [{"frame_id": "F1", "arguments": []}]}
        result = resolve_semantic_role_candidates(mapping, [])
        self.assertEqual(result["status"], "mapped")
        self.assertEqual(result["context_resolution"]["status"], "not_needed")

    def test_input_result_is_not_mutated(self):
        mapping = ambiguous_result()
        before = repr(mapping)
        resolve_semantic_role_candidates(mapping, [])
        self.assertEqual(repr(mapping), before)


if __name__ == "__main__":
    unittest.main()

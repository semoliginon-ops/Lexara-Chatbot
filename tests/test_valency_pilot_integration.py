"""Integration checks for the four approved per-sense valency pilot annotations.

These tests check parser syntax and annotation compatibility. They do not
claim that the parser currently resolves semantic roles or passive voice.
"""
from pathlib import Path
import unittest

from tools.kamus_loader import load_batch
from tools.parser_kalimat import parse_sentence


ROOT = Path(__file__).resolve().parents[1]


def token(value, pos):
    return {
        "token": value,
        "kind": "word",
        "pos": [pos],
        "pos_status": "identified",
        "context_pos": None,
        "pos_context_status": None,
    }


def parse(*items):
    return parse_sentence({"tokens": [token(value, pos) for value, pos in items]})


def load_pilot_entry(batch_name, entry_id):
    entries = load_batch(ROOT / "data" / "kamus" / batch_name)
    matches = [entry for entry in entries if entry["id"] == entry_id]
    if len(matches) != 1:
        raise AssertionError(f"Expected exactly one {entry_id}, got {len(matches)}")
    return matches[0]


class ValencyPilotIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.muncul = load_pilot_entry("batch-030.jsonl", "K1475")
        cls.lihat = load_pilot_entry("batch-001.jsonl", "K0034")
        cls.makan = load_pilot_entry("batch-001.jsonl", "K0013")
        cls.buka = load_pilot_entry("batch-002.jsonl", "K0065")

    def test_muncul_annotation_does_not_make_parser_guess_postverbal_subject(self):
        sense = self.muncul["senses"][0]
        self.assertEqual(sense["sense_id"], "K1475-S1")
        self.assertEqual(
            sense["valency_frames"][0]["arguments"][0]["semantic_role"],
            "THEME",
        )

        result = parse(("muncul", "VERB"), ("masalah", "NOUN"))
        self.assertEqual(result["status"], "unresolved")
        self.assertEqual(result["roles"]["subject"], [])
        self.assertEqual(result["roles"]["object"], [])
        self.assertIn("inversi", result["notes"][0])

    def test_lihat_parser_svo_is_consistent_with_experiencer_theme_annotation(self):
        sense = self.lihat["senses"][0]
        roles = {
            argument["syntactic_role"]: argument["semantic_role"]
            for argument in sense["valency_frames"][0]["arguments"]
        }
        self.assertEqual(roles, {"SUBJ": "EXPERIENCER", "OBJ": "THEME"})

        result = parse(
            ("Rina", "NOUN"), ("melihat", "VERB"), ("burung", "NOUN")
        )
        self.assertEqual(result["status"], "parsed")
        self.assertEqual(result["pattern"], "S-P-O")
        self.assertEqual(result["roles"]["subject"], ["Rina"])
        self.assertEqual(result["roles"]["object"], ["burung"])

    def test_buka_agent_and_causer_frames_are_both_preserved_for_same_syntax(self):
        sense = self.buka["senses"][0]
        frames = sense["valency_frames"]
        self.assertEqual(len(frames), 2)

        subject_roles = {
            next(a["semantic_role"] for a in frame["arguments"]
                 if a["syntactic_role"] == "SUBJ")
            for frame in frames
        }
        self.assertEqual(subject_roles, {"AGENT", "CAUSER"})

        agentive = parse(
            ("Rina", "NOUN"), ("membuka", "VERB"), ("pintu", "NOUN")
        )
        causal = parse(
            ("Angin", "NOUN"), ("membuka", "VERB"), ("pintu", "NOUN")
        )
        for result in (agentive, causal):
            self.assertEqual(result["status"], "parsed")
            self.assertEqual(result["pattern"], "S-P-O")
            self.assertEqual(result["roles"]["object"], ["pintu"])

        # The current parser exposes syntax only; it must not invent an
        # AGENT/CAUSER decision from the subject position.
        self.assertEqual(agentive["roles"]["subject"], ["Rina"])
        self.assertEqual(causal["roles"]["subject"], ["Angin"])
        self.assertNotIn("semantic_roles", agentive)
        self.assertNotIn("semantic_roles", causal)

    def test_makan_object_is_optional_in_annotation_and_both_surface_patterns_parse(self):
        sense = self.makan["senses"][0]
        arguments = sense["valency_frames"][0]["arguments"]
        object_argument = next(a for a in arguments if a["syntactic_role"] == "OBJ")
        self.assertFalse(object_argument["required"])

        without_object = parse(("Rina", "NOUN"), ("makan", "VERB"))
        with_object = parse(
            ("Rina", "NOUN"), ("makan", "VERB"), ("nasi", "NOUN")
        )
        self.assertEqual(without_object["status"], "parsed")
        self.assertEqual(without_object["pattern"], "S-P")
        self.assertEqual(without_object["roles"]["object"], [])
        self.assertEqual(with_object["status"], "parsed")
        self.assertEqual(with_object["pattern"], "S-P-O")
        self.assertEqual(with_object["roles"]["object"], ["nasi"])

    def test_active_and_passive_surface_roles_are_parsed_without_semantic_relabeling(self):
        active = parse(
            ("Rina", "NOUN"), ("membuka", "VERB"), ("pintu", "NOUN")
        )
        passive = parse(
            ("Pintu", "NOUN"), ("dibuka", "VERB"), ("Rina", "NOUN")
        )
        self.assertEqual(active["status"], "parsed")
        self.assertEqual(passive["status"], "parsed")
        self.assertEqual(active["roles"]["subject"], ["Rina"])
        self.assertEqual(active["roles"]["object"], ["pintu"])
        self.assertEqual(passive["roles"]["subject"], ["Pintu"])
        self.assertEqual(passive["roles"]["object"], ["Rina"])

        # Passive semantic-role remapping (PATIENT subject / AGENT oblique)
        # is deliberately not inferred by parser v1.9 or this pilot schema.
        self.assertNotIn("semantic_roles", active)
        self.assertNotIn("semantic_roles", passive)


if __name__ == "__main__":
    unittest.main()

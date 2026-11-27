"""Tests for conservative mapping from parser roles to valency semantic roles."""
from pathlib import Path
import unittest

from tools.kamus_loader import load_batch
from tools.parser_kalimat import parse_sentence
from tools.pemetaan_peran_semantis import map_semantic_roles


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


def pilot_sense(batch_name, entry_id):
    entries = load_batch(ROOT / "data" / "kamus" / batch_name)
    entry = next(item for item in entries if item["id"] == entry_id)
    return entry["senses"][0]


class SemanticRoleMappingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.muncul = pilot_sense("batch-030.jsonl", "K1475")
        cls.lihat = pilot_sense("batch-001.jsonl", "K0034")
        cls.makan = pilot_sense("batch-001.jsonl", "K0013")
        cls.buka = pilot_sense("batch-002.jsonl", "K0065")

    def test_maps_lihat_experiencer_and_theme_for_active_svo(self):
        parsed = parse(("Rina", "NOUN"), ("melihat", "VERB"), ("burung", "NOUN"))
        result = map_semantic_roles(parsed, self.lihat, voice="active")
        self.assertEqual(result["status"], "mapped")
        arguments = result["candidates"][0]["arguments"]
        self.assertEqual(
            [(a["syntactic_role"], a["semantic_role"], a["value"]) for a in arguments],
            [("SUBJ", "EXPERIENCER", ["Rina"]), ("OBJ", "THEME", ["burung"])],
        )

    def test_keeps_agent_and_causer_frames_ambiguous_for_same_buka_syntax(self):
        parsed = parse(("Angin", "NOUN"), ("membuka", "VERB"), ("pintu", "NOUN"))
        result = map_semantic_roles(parsed, self.buka, voice="active")
        self.assertEqual(result["status"], "ambiguous")
        self.assertEqual(
            {
                next(a["semantic_role"] for a in frame["arguments"]
                     if a["syntactic_role"] == "SUBJ")
                for frame in result["candidates"]
            },
            {"AGENT", "CAUSER"},
        )

    def test_accepts_makan_without_optional_object(self):
        parsed = parse(("Rina", "NOUN"), ("makan", "VERB"))
        result = map_semantic_roles(parsed, self.makan, voice="active")
        self.assertEqual(result["status"], "mapped")
        obj = next(a for a in result["candidates"][0]["arguments"]
                   if a["syntactic_role"] == "OBJ")
        self.assertEqual(obj["presence"], "omitted")
        self.assertEqual(obj["semantic_role"], "PATIENT")
        self.assertEqual(obj["value"], [])

    def test_maps_optional_makan_object_when_present(self):
        parsed = parse(("Rina", "NOUN"), ("makan", "VERB"), ("nasi", "NOUN"))
        result = map_semantic_roles(parsed, self.makan, voice="active")
        self.assertEqual(result["status"], "mapped")
        obj = next(a for a in result["candidates"][0]["arguments"]
                   if a["syntactic_role"] == "OBJ")
        self.assertEqual(obj["presence"], "present")
        self.assertEqual(obj["value"], ["nasi"])

    def test_does_not_map_when_voice_is_not_confirmed(self):
        parsed = parse(("Rina", "NOUN"), ("membuka", "VERB"), ("pintu", "NOUN"))
        result = map_semantic_roles(parsed, self.buka)
        self.assertEqual(result["status"], "unresolved")
        self.assertEqual(result["reason"], "voice_not_confirmed")
        self.assertEqual(result["candidates"], [])

    def test_maps_passive_with_postverbal_agent(self):
        parsed = parse(("Pintu", "NOUN"), ("dibuka", "VERB"), ("Rina", "NOUN"))
        self.assertEqual(parsed["status"], "parsed")
        result = map_semantic_roles(parsed, self.buka, voice="passive")
        self.assertEqual(result["status"], "ambiguous")
        self.assertEqual(
            {
                tuple((a["semantic_role"], tuple(a["value"]), a["realization"])
                      for a in frame["arguments"])
                for frame in result["candidates"]
            },
            {
                (("AGENT", ("Rina",), "postverbal_agent"),
                 ("PATIENT", ("Pintu",), "passive_surface_subject")),
                (("CAUSER", ("Rina",), "postverbal_agent"),
                 ("PATIENT", ("Pintu",), "passive_surface_subject")),
            },
        )

    def test_maps_passive_with_oleh_agent_phrase(self):
        parsed = parse(
            ("Pintu", "NOUN"), ("dibuka", "VERB"),
            ("oleh", "PREP"), ("Rina", "NOUN"),
        )
        self.assertEqual(parsed["status"], "parsed")
        result = map_semantic_roles(parsed, self.buka, voice="passive")
        self.assertEqual(result["status"], "ambiguous")
        for frame in result["candidates"]:
            agent = frame["arguments"][0]
            patient = frame["arguments"][1]
            self.assertEqual(agent["value"], ["Rina"])
            self.assertEqual(agent["realization"], "oleh_phrase")
            self.assertEqual(patient["semantic_role"], "PATIENT")
            self.assertEqual(patient["value"], ["Pintu"])

    def test_maps_agentless_passive_and_marks_agent_omitted(self):
        parsed = parse(("Pintu", "NOUN"), ("dibuka", "VERB"))
        self.assertEqual(parsed["status"], "parsed")
        result = map_semantic_roles(parsed, self.buka, voice="passive")
        self.assertEqual(result["status"], "ambiguous")
        for frame in result["candidates"]:
            agent = frame["arguments"][0]
            self.assertEqual(agent["presence"], "omitted")
            self.assertEqual(agent["value"], [])
            self.assertEqual(agent["realization"], "omitted")
            self.assertEqual(frame["arguments"][1]["value"], ["Pintu"])

    def test_does_not_guess_when_passive_agent_realizations_conflict(self):
        parsed = parse(
            ("Pintu", "NOUN"), ("dibuka", "VERB"), ("Rina", "NOUN"),
            ("oleh", "PREP"), ("Budi", "NOUN"),
        )
        result = map_semantic_roles(parsed, self.buka, voice="passive")
        self.assertEqual(result["status"], "unresolved")
        self.assertEqual(result["reason"], "passive_agent_realization_conflict")

    def test_does_not_map_unresolved_postverbal_inversion(self):
        parsed = parse(("muncul", "VERB"), ("masalah", "NOUN"))
        result = map_semantic_roles(parsed, self.muncul, voice="active")
        self.assertEqual(result["status"], "unresolved")
        self.assertEqual(result["reason"], "parser_not_fully_resolved")

    def test_required_object_missing_makes_lihat_frame_incompatible(self):
        parsed = parse(("Rina", "NOUN"), ("melihat", "VERB"))
        result = map_semantic_roles(parsed, self.lihat, voice="active")
        self.assertEqual(result["status"], "incompatible")
        self.assertEqual(result["reason"], "no_frame_matches_surface_roles")

    def test_maps_oblique_only_when_preposition_constraint_matches(self):
        sense = {
            "sense_id": "pergi-test-S1",
            "valency_frames": [{
                "frame_id": "F1",
                "arguments": [
                    {
                        "argument_id": "A1",
                        "syntactic_role": "SUBJ",
                        "semantic_role": "AGENT",
                        "required": True,
                        "realizations": [{"type": "NP"}],
                    },
                    {
                        "argument_id": "A2",
                        "syntactic_role": "OBL",
                        "semantic_role": "GOAL",
                        "required": True,
                        "realizations": [{"type": "PP", "prepositions": ["ke"]}],
                    },
                ],
            }],
        }
        parsed = parse(
            ("Rina", "NOUN"), ("pergi", "VERB"),
            ("ke", "PREP"), ("pasar", "NOUN"),
        )
        result = map_semantic_roles(parsed, sense, voice="active")
        self.assertEqual(result["status"], "mapped")
        oblique = result["candidates"][0]["arguments"][1]
        self.assertEqual(oblique["semantic_role"], "GOAL")
        self.assertEqual(oblique["value"], [{"preposition": "ke", "phrase": ["pasar"]}])

    def test_rejects_oblique_with_nonmatching_preposition(self):
        sense = {
            "sense_id": "pergi-test-S1",
            "valency_frames": [{
                "frame_id": "F1",
                "arguments": [
                    {
                        "argument_id": "A1",
                        "syntactic_role": "SUBJ",
                        "semantic_role": "AGENT",
                        "required": True,
                        "realizations": [{"type": "NP"}],
                    },
                    {
                        "argument_id": "A2",
                        "syntactic_role": "OBL",
                        "semantic_role": "SOURCE",
                        "required": True,
                        "realizations": [{"type": "PP", "prepositions": ["dari"]}],
                    },
                ],
            }],
        }
        parsed = parse(
            ("Rina", "NOUN"), ("pergi", "VERB"),
            ("ke", "PREP"), ("pasar", "NOUN"),
        )
        result = map_semantic_roles(parsed, sense, voice="active")
        self.assertEqual(result["status"], "incompatible")


    def test_rejects_frame_that_ignores_recognized_object(self):
        parsed = parse(
            ("Rina", "NOUN"), ("membuka", "VERB"), ("pintu", "NOUN")
        )
        intransitive_sense = {
            "sense_id": "uji-intransitif-S1",
            "valency_frames": [{
                "frame_id": "F1",
                "arguments": [{
                    "argument_id": "A1",
                    "syntactic_role": "SUBJ",
                    "semantic_role": "THEME",
                    "required": True,
                    "realizations": [{"type": "NP"}],
                }],
            }],
        }
        result = map_semantic_roles(parsed, intransitive_sense, voice="active")
        self.assertEqual(result["status"], "incompatible")
        self.assertEqual(result["reason"], "no_frame_matches_surface_roles")

    def test_does_not_map_unconstrained_oblique_as_core_argument(self):
        parsed = parse(
            ("Rina", "NOUN"), ("pergi", "VERB"),
            ("ke", "PREP"), ("pasar", "NOUN"),
        )
        unconstrained_sense = {
            "sense_id": "pergi-tanpa-batas-S1",
            "valency_frames": [{
                "frame_id": "F1",
                "arguments": [
                    {
                        "argument_id": "A1",
                        "syntactic_role": "SUBJ",
                        "semantic_role": "AGENT",
                        "required": True,
                        "realizations": [{"type": "NP"}],
                    },
                    {
                        "argument_id": "A2",
                        "syntactic_role": "OBL",
                        "semantic_role": "GOAL",
                        "required": True,
                        "realizations": [{"type": "PP"}],
                    },
                ],
            }],
        }
        result = map_semantic_roles(parsed, unconstrained_sense, voice="active")
        self.assertEqual(result["status"], "incompatible")
        self.assertEqual(result["reason"], "no_frame_matches_surface_roles")


    def test_preserves_causer_instrument_ambiguity_without_context(self):
        parsed = parse(
            ("Palu", "NOUN"), ("memecahkan", "VERB"), ("kaca", "NOUN")
        )
        ambiguous_sense = {
            "sense_id": "memecahkan-uji-S1",
            "valency_frames": [
                {
                    "frame_id": "F_CAUSER",
                    "arguments": [
                        {
                            "argument_id": "A1",
                            "syntactic_role": "SUBJ",
                            "semantic_role": "CAUSER",
                            "required": True,
                            "realizations": [{"type": "NP"}],
                        },
                        {
                            "argument_id": "A2",
                            "syntactic_role": "OBJ",
                            "semantic_role": "PATIENT",
                            "required": True,
                            "realizations": [{"type": "NP"}],
                        },
                    ],
                },
                {
                    "frame_id": "F_INSTRUMENT",
                    "arguments": [
                        {
                            "argument_id": "A1",
                            "syntactic_role": "SUBJ",
                            "semantic_role": "INSTRUMENT",
                            "required": True,
                            "realizations": [{"type": "NP"}],
                        },
                        {
                            "argument_id": "A2",
                            "syntactic_role": "OBJ",
                            "semantic_role": "PATIENT",
                            "required": True,
                            "realizations": [{"type": "NP"}],
                        },
                    ],
                },
            ],
        }
        result = map_semantic_roles(parsed, ambiguous_sense, voice="active")
        self.assertEqual(result["status"], "ambiguous")
        subject_roles = {
            next(a["semantic_role"] for a in frame["arguments"]
                 if a["syntactic_role"] == "SUBJ")
            for frame in result["candidates"]
        }
        self.assertEqual(subject_roles, {"CAUSER", "INSTRUMENT"})

    def test_does_not_promote_instrument_adjunct_to_core_oblique(self):
        parsed = parse(
            ("Rina", "NOUN"), ("memecahkan", "VERB"), ("kaca", "NOUN"),
            ("dengan", "PREP"), ("palu", "NOUN"),
        )
        sense = {
            "sense_id": "memecahkan-uji-argumen-S1",
            "valency_frames": [{
                "frame_id": "F1",
                "arguments": [
                    {
                        "argument_id": "A1",
                        "syntactic_role": "SUBJ",
                        "semantic_role": "AGENT",
                        "required": True,
                        "realizations": [{"type": "NP"}],
                    },
                    {
                        "argument_id": "A2",
                        "syntactic_role": "OBJ",
                        "semantic_role": "PATIENT",
                        "required": True,
                        "realizations": [{"type": "NP"}],
                    },
                ],
            }],
        }
        result = map_semantic_roles(parsed, sense, voice="active")
        self.assertEqual(result["status"], "mapped")
        mapped_roles = {
            argument["semantic_role"]
            for frame in result["candidates"]
            for argument in frame["arguments"]
        }
        self.assertEqual(mapped_roles, {"AGENT", "PATIENT"})
        self.assertNotIn("INSTRUMENT", mapped_roles)

    def test_rejects_invalid_voice_value(self):
        with self.assertRaises(ValueError):
            map_semantic_roles({}, self.buka, voice="middle")


if __name__ == "__main__":
    unittest.main()

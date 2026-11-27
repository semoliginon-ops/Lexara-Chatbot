"""Regression tests for per-sense valency metadata validation."""
import unittest

from tools.validasi_valensi import (
    validate_entries_valency,
    validate_entry_valency,
)


def legacy_entry():
    return {
        "id": "K0001",
        "lemma": "muncul",
        "pos": ["VERB"],
        "senses": [{"sense_id": "K0001-S1", "definition": "Mulai hadir."}],
        "register": ["neutral"],
    }


def valid_frame():
    return {
        "frame_id": "F1",
        "arguments": [
            {
                "argument_id": "A1",
                "syntactic_role": "SUBJ",
                "semantic_role": "THEME",
                "required": True,
                "realizations": [{"type": "NP"}],
            }
        ],
    }


class ValencyValidationTests(unittest.TestCase):
    def test_accepts_legacy_entry_without_valency_metadata(self):
        self.assertEqual(validate_entry_valency(legacy_entry()), [])

    def test_accepts_valid_frame_with_approved_semantic_role(self):
        entry = legacy_entry()
        entry["senses"][0]["valency_frames"] = [valid_frame()]
        self.assertEqual(validate_entry_valency(entry), [])

    def test_accepts_unannotated_semantic_role(self):
        entry = legacy_entry()
        frame = valid_frame()
        frame["arguments"][0]["semantic_role"] = None
        entry["senses"][0]["valency_frames"] = [frame]
        self.assertEqual(validate_entry_valency(entry), [])

    def test_accepts_pp_preposition_constraints(self):
        entry = legacy_entry()
        frame = valid_frame()
        frame["arguments"][0].update({
            "syntactic_role": "OBL",
            "semantic_role": "RECIPIENT",
            "realizations": [{"type": "PP", "prepositions": ["kepada", "ke"]}],
        })
        entry["senses"][0]["valency_frames"] = [frame]
        self.assertEqual(validate_entry_valency(entry), [])

    def test_rejects_missing_sense_id(self):
        entry = legacy_entry()
        del entry["senses"][0]["sense_id"]
        entry["senses"][0]["valency_frames"] = [valid_frame()]
        errors = validate_entry_valency(entry)
        self.assertTrue(any("sense_id wajib" in error for error in errors))

    def test_rejects_empty_frames_and_arguments(self):
        entry = legacy_entry()
        entry["senses"][0]["valency_frames"] = []
        errors = validate_entry_valency(entry)
        self.assertTrue(any("valency_frames" in error for error in errors))
        entry["senses"][0]["valency_frames"] = [{"frame_id": "F1", "arguments": []}]
        errors = validate_entry_valency(entry)
        self.assertTrue(any("arguments" in error for error in errors))

    def test_rejects_duplicate_frame_and_argument_ids(self):
        entry = legacy_entry()
        first = valid_frame()
        second = valid_frame()
        first["arguments"].append(dict(first["arguments"][0]))
        entry["senses"][0]["valency_frames"] = [first, second]
        errors = validate_entry_valency(entry)
        self.assertTrue(any("frame_id: duplikat" in error for error in errors))
        self.assertTrue(any("argument_id: duplikat" in error for error in errors))

    def test_rejects_unknown_syntactic_and_semantic_roles(self):
        entry = legacy_entry()
        frame = valid_frame()
        frame["arguments"][0]["syntactic_role"] = "SUBJECT"
        frame["arguments"][0]["semantic_role"] = "DOER"
        entry["senses"][0]["valency_frames"] = [frame]
        errors = validate_entry_valency(entry)
        self.assertTrue(any("syntactic_role" in error for error in errors))
        self.assertTrue(any("semantic_role" in error for error in errors))

    def test_requires_semantic_role_field_even_when_null_is_allowed(self):
        entry = legacy_entry()
        frame = valid_frame()
        del frame["arguments"][0]["semantic_role"]
        entry["senses"][0]["valency_frames"] = [frame]
        self.assertTrue(any("semantic_role: field wajib" in e for e in validate_entry_valency(entry)))

    def test_rejects_non_boolean_required(self):
        entry = legacy_entry()
        frame = valid_frame()
        frame["arguments"][0]["required"] = "true"
        entry["senses"][0]["valency_frames"] = [frame]
        self.assertTrue(any("required: harus berupa boolean" in e for e in validate_entry_valency(entry)))

    def test_rejects_prepositions_on_non_pp_realization(self):
        entry = legacy_entry()
        frame = valid_frame()
        frame["arguments"][0]["realizations"] = [
            {"type": "NP", "prepositions": ["kepada"]}
        ]
        entry["senses"][0]["valency_frames"] = [frame]
        self.assertTrue(any("hanya boleh digunakan" in e for e in validate_entry_valency(entry)))

    def test_rejects_blank_and_duplicate_prepositions(self):
        entry = legacy_entry()
        frame = valid_frame()
        frame["arguments"][0]["realizations"] = [
            {"type": "PP", "prepositions": ["ke", " KE ", ""]}
        ]
        entry["senses"][0]["valency_frames"] = [frame]
        errors = validate_entry_valency(entry)
        self.assertTrue(any("preposisi duplikat" in e for e in errors))
        self.assertTrue(any("teks nonkosong" in e for e in errors))

    def test_rejects_duplicate_realizations_and_unknown_fields(self):
        entry = legacy_entry()
        frame = valid_frame()
        frame["unexpected"] = True
        frame["arguments"][0]["realizations"] = [{"type": "NP"}, {"type": "NP"}]
        entry["senses"][0]["valency_frames"] = [frame]
        errors = validate_entry_valency(entry)
        self.assertTrue(any("field tidak dikenal" in e for e in errors))
        self.assertTrue(any("realisasi duplikat" in e for e in errors))

    def test_rejects_invalid_realization_type(self):
        entry = legacy_entry()
        frame = valid_frame()
        frame["arguments"][0]["realizations"] = [{"type": "WORD"}]
        entry["senses"][0]["valency_frames"] = [frame]
        self.assertTrue(any(".type: nilai tidak dikenal" in e for e in validate_entry_valency(entry)))

    def test_reports_entry_id_for_collection_validation(self):
        good = legacy_entry()
        bad = legacy_entry()
        bad["id"] = "K0002"
        bad["senses"][0]["valency_frames"] = [{"frame_id": "", "arguments": []}]
        errors = validate_entries_valency([good, bad])
        self.assertTrue(errors)
        self.assertTrue(all("K0002" in error for error in errors))


if __name__ == "__main__":
    unittest.main()

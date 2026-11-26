"""Regression tests for tools.normalisasi."""
import unittest

from tools.normalisasi import normalize_text


class NormalizeTextTests(unittest.TestCase):
    def test_lowercases_text(self):
        self.assertEqual(normalize_text("AKU MAU MAKAN"), "aku mau makan")

    def test_collapses_and_trims_whitespace(self):
        self.assertEqual(normalize_text("  aku\t\n mau   makan  "), "aku mau makan")

    def test_preserves_punctuation(self):
        self.assertEqual(normalize_text("GAK MAU!!!, SERIUS?"), "gak mau!!!, serius?")

    def test_preserves_hyphens_and_apostrophes(self):
        self.assertEqual(normalize_text("Makan-makan 'ku'"), "makan-makan 'ku'")

    def test_preserves_informal_vocabulary(self):
        self.assertEqual(normalize_text("Gue mager banget"), "gue mager banget")

    def test_normalizes_unicode_to_nfc(self):
        decomposed = "cafe\u0301"
        self.assertEqual(normalize_text(decomposed), "café")

    def test_empty_and_whitespace_only_strings(self):
        self.assertEqual(normalize_text(""), "")
        self.assertEqual(normalize_text(" \t\n "), "")

    def test_rejects_non_string_input(self):
        with self.assertRaises(TypeError):
            normalize_text(None)


if __name__ == "__main__":
    unittest.main()

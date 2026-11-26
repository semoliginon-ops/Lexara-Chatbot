"""Regression tests for tools.tokenizer."""
import unittest

from tools.tokenizer import tokenize


class TokenizerTests(unittest.TestCase):
    def test_splits_simple_sentence(self):
        self.assertEqual(
            tokenize("Aku mau makan nasi!"),
            ["aku", "mau", "makan", "nasi", "!"],
        )

    def test_preserves_repeated_punctuation_as_separate_tokens(self):
        self.assertEqual(tokenize("Serius?!"), ["serius", "?", "!"])

    def test_collapses_whitespace_through_normalization(self):
        self.assertEqual(tokenize("  Aku\t mau\n makan  "), ["aku", "mau", "makan"])

    def test_keeps_hyphenated_words_together(self):
        self.assertEqual(tokenize("Anak-anak makan-makan"), ["anak-anak", "makan-makan"])

    def test_keeps_internal_apostrophes(self):
        self.assertEqual(tokenize("ku'u dan 'ku'"), ["ku'u", "'", "ku", "'"])

    def test_keeps_curly_apostrophe_inside_word(self):
        self.assertEqual(tokenize("Jum’at"), ["jum’at"])

    def test_handles_numbers(self):
        self.assertEqual(tokenize("Aku punya 25 buku."), ["aku", "punya", "25", "buku", "."])

    def test_splits_punctuation_around_words(self):
        self.assertEqual(tokenize("(Halo), dunia!"), ["(", "halo", ")", ",", "dunia", "!"])

    def test_empty_and_whitespace_only_input(self):
        self.assertEqual(tokenize(""), [])
        self.assertEqual(tokenize(" \t\n "), [])

    def test_preserves_informal_words(self):
        self.assertEqual(tokenize("GUE gak mau!!!"), ["gue", "gak", "mau", "!", "!", "!"])

    def test_underscore_is_not_absorbed_into_word(self):
        self.assertEqual(tokenize("nama_pengguna"), ["nama", "_", "pengguna"])

    def test_rejects_non_string_input(self):
        with self.assertRaises(TypeError):
            tokenize(None)


if __name__ == "__main__":
    unittest.main()

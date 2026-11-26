"""Regression tests for tools.pencocokan_kamus."""
import unittest

from tools.pencocokan_kamus import (
    LexiconBuildError,
    build_lexicon,
    lookup_token,
)


def entry(entry_id="K0001", lemma="makan", **extra):
    result = {
        "id": entry_id,
        "lemma": lemma,
        "pos": ["VERB"],
        "senses": [
            {"sense_id": f"{entry_id}-S1", "definition": "Makna pertama."},
            {"sense_id": f"{entry_id}-S2", "definition": "Makna kedua."},
        ],
        "register": ["neutral"],
        "variants": [],
        "derived_forms": [],
    }
    result.update(extra)
    return result


class LexiconMatchingTests(unittest.TestCase):
    def test_matches_lemma(self):
        lexicon = build_lexicon([entry()])
        result = lookup_token("makan", lexicon)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["match_type"], "lemma")

    def test_matches_variant(self):
        lexicon = build_lexicon([entry(variants=["mkn"])])
        result = lookup_token("mkn", lexicon)
        self.assertEqual(result[0]["match_type"], "variant")
        self.assertEqual(result[0]["lemma"], "makan")

    def test_matches_derived_form(self):
        lexicon = build_lexicon([entry(derived_forms=["memakan"])])
        result = lookup_token("memakan", lexicon)
        self.assertEqual(result[0]["match_type"], "derived_form")

    def test_lookup_is_case_insensitive(self):
        lexicon = build_lexicon([entry(lemma="Makan")])
        self.assertEqual(len(lookup_token("MAKAN", lexicon)), 1)

    def test_lookup_uses_unicode_nfc(self):
        composed = "é"
        decomposed = "e\u0301"
        lexicon = build_lexicon([entry(lemma=composed)])
        self.assertEqual(len(lookup_token(decomposed, lexicon)), 1)

    def test_unknown_token_returns_empty_list(self):
        lexicon = build_lexicon([entry()])
        self.assertEqual(lookup_token("berlari", lexicon), [])

    def test_empty_token_returns_empty_list(self):
        self.assertEqual(lookup_token("   ", build_lexicon([entry()])), [])

    def test_preserves_all_senses_and_pos(self):
        original = entry()
        result = lookup_token("makan", build_lexicon([original]))
        self.assertIs(result[0]["entry"], original)
        self.assertEqual(len(result[0]["entry"]["senses"]), 2)
        self.assertEqual(result[0]["entry"]["pos"], ["VERB"])

    def test_returns_all_candidates_for_shared_key(self):
        first = entry("K0001", "bisa")
        second = entry("K0002", "bisa")
        result = lookup_token("bisa", build_lexicon([first, second]))
        self.assertEqual([item["entry_id"] for item in result], ["K0001", "K0002"])

    def test_optional_form_fields_may_be_absent(self):
        original = {"id": "K0001", "lemma": "rumah"}
        self.assertEqual(len(lookup_token("rumah", build_lexicon([original]))), 1)

    def test_rejects_non_dictionary_entry(self):
        with self.assertRaises(LexiconBuildError):
            build_lexicon(["not-an-entry"])

    def test_rejects_invalid_forms_array(self):
        with self.assertRaisesRegex(LexiconBuildError, "variants harus"):
            build_lexicon([entry(variants="bukan-array")])

    def test_rejects_non_string_lookup_token(self):
        with self.assertRaises(TypeError):
            lookup_token(123, build_lexicon([entry()]))


if __name__ == "__main__":
    unittest.main()

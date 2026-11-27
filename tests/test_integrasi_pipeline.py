"""End-to-end integration tests using the complete dictionary."""
from pathlib import Path
import unittest

from tools.analisis_teks import analyze_text
from tools.kamus_loader import load_dictionary_directory
from tools.pencocokan_kamus import build_lexicon
from tools.pos_context import disambiguate_pos_context
from tools.pos_tagger import tag_pos
from tools.parser_kalimat import parse_sentence


ROOT = Path(__file__).resolve().parents[1]


class FullDictionaryPipelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.entries = load_dictionary_directory(ROOT / "data" / "kamus")
        cls.lexicon = build_lexicon(cls.entries)

    def analyze(self, text):
        lexical = analyze_text(text, self.lexicon)
        tagged = tag_pos(lexical)
        return disambiguate_pos_context(tagged)

    @staticmethod
    def token(result, surface):
        return next(item for item in result["tokens"] if item["token"] == surface)

    def test_loads_full_dictionary_without_duplicate_lemmas(self):
        self.assertEqual(len(self.entries), 3025)
        self.assertGreater(len(self.lexicon), 3000)
        self.assertIn("aku", self.lexicon)
        self.assertIn("rumah", self.lexicon)

    def test_akan_is_adverb_from_dictionary_and_only_modal_with_lexical_verb(self):
        entry = next(item for item in self.entries if item["lemma"] == "akan")
        self.assertEqual(entry["id"], "K3015")
        self.assertEqual(entry["pos"], ["ADV"])
        self.assertEqual(
            entry["senses"][0]["definition"],
            "Menandakan sesuatu akan terjadi di masa depan; penanda aspek masa mendatang.",
        )

        for sentence in ("Aku akan pergi besok.", "Dia akan makan nasi."):
            with self.subTest(sentence=sentence):
                result = self.analyze(sentence)
                token = self.token(result, "akan")
                self.assertEqual(token["status"], "matched")
                self.assertEqual(token["pos"], ["ADV"])
                self.assertEqual(token["pos_source"], "dictionary")
                self.assertEqual(token["pos_status"], "identified")

        parsed = parse_sentence(self.analyze("Dia akan makan nasi."))
        self.assertEqual(parsed["status"], "parsed")
        self.assertEqual(parsed["pattern"], "S-P-O")
        self.assertEqual(parsed["roles"]["predicate"], ["akan", "makan"])
        self.assertEqual(parsed["predicate_structure"]["head"], "makan")
        self.assertIn(
            {"token": "akan", "kind": "modal"},
            parsed["predicate_structure"]["modifiers"],
        )
        self.assertEqual(parsed["roles"]["object"], ["nasi"])

        standalone = self.analyze("Aku akan.")
        self.assertEqual(self.token(standalone, "akan")["pos"], ["ADV"])
        cautious = parse_sentence(standalone)
        self.assertEqual(cautious["status"], "unresolved")
        self.assertEqual(cautious["roles"]["predicate"], [])

    def test_explicit_derived_form_pos_survives_full_pipeline(self):
        expected = {
            "bekerja": ("kerja", "VERB"),
            "menjelaskan": ("jelas", "VERB"),
            "letakkan": ("letak", "VERB"),
            "terdengar": ("dengar", "VERB"),
        }
        for surface, (lemma, pos) in expected.items():
            with self.subTest(surface=surface):
                result = self.analyze(surface)
                item = self.token(result, surface)
                self.assertEqual(item["status"], "matched")
                self.assertEqual(item["pos"], [pos])
                self.assertEqual(item["pos_source"], "dictionary")
                self.assertEqual(item["pos_status"], "identified")
                self.assertTrue(
                    any(candidate["lemma"] == lemma for candidate in item["candidates"])
                )

    def test_pandang_and_tanding_derived_forms_keep_audited_surface_pos(self):
        expected = {
            "memandang": ("pandang", "VERB"),
            "dipandang": ("pandang", "VERB"),
            "pandangan": ("pandang", "NOUN"),
            "pemandangan": ("pandang", "NOUN"),
            "bertanding": ("tanding", "VERB"),
            "pertandingan": ("tanding", "NOUN"),
            "menandingi": ("tanding", "VERB"),
        }
        for surface, (lemma, pos) in expected.items():
            with self.subTest(surface=surface):
                item = self.token(self.analyze(surface), surface)
                self.assertEqual(item["status"], "matched")
                self.assertEqual(item["pos"], [pos])
                self.assertTrue(
                    any(candidate["lemma"] == lemma for candidate in item["candidates"])
                )

    def test_pak_pelajaran_and_adiknya_have_explicit_pos(self):
        result = self.analyze("pak memberi pelajaran kepada adiknya")
        expected = {
            "pak": ("NOUN", "supplement"),
            "pelajaran": ("NOUN", "dictionary"),
            "adiknya": ("NOUN", "dictionary"),
        }
        for surface, (pos, source) in expected.items():
            with self.subTest(surface=surface):
                item = self.token(result, surface)
                self.assertEqual(item["pos"], [pos])
                self.assertEqual(item["pos_source"], source)
                self.assertEqual(item["pos_status"], "identified")
        for surface, lemma in (("pelajaran", "ajar"), ("adiknya", "adik")):
            item = self.token(result, surface)
            self.assertTrue(
                any(candidate["lemma"] == lemma for candidate in item["candidates"])
            )

    def test_context_resolves_real_dictionary_ambiguity_conservatively(self):
        verb_result = self.analyze("sedang jalan")
        verb = self.token(verb_result, "jalan")
        self.assertEqual(verb["pos"], ["NOUN", "VERB"])
        self.assertEqual(verb["context_pos"], "VERB")
        self.assertEqual(verb["pos_context_status"], "selected_by_context")

        noun_result = self.analyze("di jalan")
        noun = self.token(noun_result, "jalan")
        self.assertEqual(noun["pos"], ["NOUN", "VERB"])
        self.assertEqual(noun["context_pos"], "NOUN")
        self.assertEqual(noun["pos_context_status"], "selected_by_context")

    def test_ambiguity_is_not_forced_without_context(self):
        item = self.token(self.analyze("jalan"), "jalan")
        self.assertEqual(item["pos"], ["NOUN", "VERB"])
        self.assertIsNone(item["context_pos"])
        self.assertEqual(item["pos_context_status"], "ambiguous")

    def test_adjectival_predicate_uses_real_dictionary_pipeline(self):
        analyzed = self.analyze("Dia sakit.")
        subject = self.token(analyzed, "dia")
        predicate = self.token(analyzed, "sakit")
        self.assertEqual(subject["pos"], ["PRON"])
        self.assertEqual(subject["pos_status"], "identified")
        self.assertEqual(predicate["pos"], ["ADJ"])
        self.assertEqual(predicate["pos_status"], "identified")

        parsed = parse_sentence(analyzed)
        self.assertEqual(parsed["status"], "parsed")
        self.assertEqual(parsed["pattern"], "S-P")
        self.assertEqual(parsed["roles"]["subject"], ["dia"])
        self.assertEqual(parsed["roles"]["predicate"], ["sakit"])
        self.assertEqual(parsed["roles"]["object"], [])

    def test_verbal_negation_uses_real_dictionary_pipeline(self):
        analyzed = self.analyze("Aku tidak makan nasi.")
        expected = {
            "aku": "PRON",
            "tidak": "ADV",
            "makan": "VERB",
            "nasi": "NOUN",
        }
        for surface, pos in expected.items():
            with self.subTest(surface=surface):
                item = self.token(analyzed, surface)
                self.assertEqual(item["pos"], [pos])
                self.assertEqual(item["pos_status"], "identified")

        parsed = parse_sentence(analyzed)
        self.assertEqual(parsed["status"], "parsed")
        self.assertEqual(parsed["pattern"], "S-P-O")
        self.assertEqual(parsed["roles"]["subject"], ["aku"])
        self.assertEqual(parsed["roles"]["predicate"], ["tidak", "makan"])
        self.assertEqual(parsed["predicate_structure"]["head"], "makan")
        self.assertIn(
            {"token": "tidak", "kind": "negation"},
            parsed["predicate_structure"]["modifiers"],
        )
        self.assertEqual(parsed["roles"]["object"], ["nasi"])

    def test_verbal_modal_predicates_use_real_dictionary_pipeline(self):
        for modal in ("mau", "ingin"):
            with self.subTest(modal=modal):
                analyzed = self.analyze(f"Aku {modal} makan nasi.")
                expected = {
                    "aku": "PRON",
                    modal: "VERB",
                    "makan": "VERB",
                    "nasi": "NOUN",
                }
                for surface, pos in expected.items():
                    with self.subTest(surface=surface):
                        item = self.token(analyzed, surface)
                        self.assertEqual(item["pos"], [pos])
                        self.assertEqual(item["pos_status"], "identified")

                parsed = parse_sentence(analyzed)
                self.assertEqual(parsed["status"], "parsed")
                self.assertEqual(parsed["pattern"], "S-P-O")
                self.assertEqual(parsed["roles"]["subject"], ["aku"])
                self.assertEqual(parsed["roles"]["predicate"], [modal, "makan"])
                self.assertEqual(parsed["predicate_structure"]["head"], "makan")
                self.assertEqual(
                    parsed["predicate_structure"]["modifiers"],
                    [{"token": modal, "kind": "modal"}],
                )
                self.assertEqual(parsed["roles"]["object"], ["nasi"])

    def test_verbal_negation_with_bisa_modal_uses_real_dictionary_pipeline(self):
        analyzed = self.analyze("Aku tidak bisa makan nasi.")
        expected = {
            "aku": "PRON",
            "tidak": "ADV",
            "makan": "VERB",
            "nasi": "NOUN",
        }
        for surface, pos in expected.items():
            with self.subTest(surface=surface):
                item = self.token(analyzed, surface)
                self.assertEqual(item["pos"], [pos])
                self.assertEqual(item["pos_status"], "identified")

        modal_token = self.token(analyzed, "bisa")
        self.assertEqual(modal_token["pos"], ["VERB", "NOUN"])
        self.assertEqual(modal_token["context_pos"], "VERB")
        self.assertEqual(modal_token["pos_context_status"], "selected_by_context")
        self.assertIn(
            {"rule": "bisa_before_verb", "pos": "VERB", "cue_token": "makan"},
            modal_token["pos_context_evidence"],
        )

        parsed = parse_sentence(analyzed)
        self.assertEqual(parsed["status"], "parsed")
        self.assertEqual(parsed["pattern"], "S-P-O")
        self.assertEqual(parsed["roles"]["subject"], ["aku"])
        self.assertEqual(parsed["roles"]["predicate"], ["tidak", "bisa", "makan"])
        self.assertEqual(parsed["predicate_structure"]["head"], "makan")
        self.assertEqual(
            parsed["predicate_structure"]["modifiers"],
            [
                {"token": "tidak", "kind": "negation"},
                {"token": "bisa", "kind": "modal"},
            ],
        )
        self.assertEqual(parsed["roles"]["object"], ["nasi"])

    def test_bisa_modal_predicate_uses_real_dictionary_pipeline(self):
        analyzed = self.analyze("Aku bisa makan nasi.")
        expected = {
            "aku": "PRON",
            "makan": "VERB",
            "nasi": "NOUN",
        }
        for surface, pos in expected.items():
            with self.subTest(surface=surface):
                item = self.token(analyzed, surface)
                self.assertEqual(item["pos"], [pos])
                self.assertEqual(item["pos_status"], "identified")

        modal_token = self.token(analyzed, "bisa")
        self.assertEqual(modal_token["pos"], ["VERB", "NOUN"])
        self.assertEqual(modal_token["context_pos"], "VERB")
        self.assertEqual(modal_token["pos_context_status"], "selected_by_context")
        self.assertIn(
            {"rule": "bisa_before_verb", "pos": "VERB", "cue_token": "makan"},
            modal_token["pos_context_evidence"],
        )

        parsed = parse_sentence(analyzed)
        self.assertEqual(parsed["status"], "parsed")
        self.assertEqual(parsed["pattern"], "S-P-O")
        self.assertEqual(parsed["roles"]["subject"], ["aku"])
        self.assertEqual(parsed["roles"]["predicate"], ["bisa", "makan"])
        self.assertEqual(parsed["predicate_structure"]["head"], "makan")
        self.assertEqual(
            parsed["predicate_structure"]["modifiers"],
            [{"token": "bisa", "kind": "modal"}],
        )
        self.assertEqual(parsed["roles"]["object"], ["nasi"])

    def test_verbal_negation_and_modal_adverb_use_real_dictionary_pipeline(self):
        analyzed = self.analyze("Aku tidak akan makan nasi.")
        expected = {
            "aku": "PRON",
            "tidak": "ADV",
            "akan": "ADV",
            "makan": "VERB",
            "nasi": "NOUN",
        }
        for surface, pos in expected.items():
            with self.subTest(surface=surface):
                item = self.token(analyzed, surface)
                self.assertEqual(item["pos"], [pos])
                self.assertEqual(item["pos_status"], "identified")

        parsed = parse_sentence(analyzed)
        self.assertEqual(parsed["status"], "parsed")
        self.assertEqual(parsed["pattern"], "S-P-O")
        self.assertEqual(parsed["roles"]["subject"], ["aku"])
        self.assertEqual(parsed["roles"]["predicate"], ["tidak", "akan", "makan"])
        self.assertEqual(parsed["predicate_structure"]["head"], "makan")
        self.assertEqual(
            parsed["predicate_structure"]["modifiers"],
            [
                {"token": "tidak", "kind": "negation"},
                {"token": "akan", "kind": "modal"},
            ],
        )
        self.assertEqual(parsed["roles"]["object"], ["nasi"])

    def test_nominal_subject_with_object_uses_real_dictionary_pipeline(self):
        analyzed = self.analyze("Anak makan nasi.")
        for surface, expected_pos in (
            ("anak", "NOUN"),
            ("makan", "VERB"),
            ("nasi", "NOUN"),
        ):
            item = self.token(analyzed, surface)
            self.assertEqual(item["pos"], [expected_pos])
            self.assertEqual(item["pos_status"], "identified")

        parsed = parse_sentence(analyzed)
        self.assertEqual(parsed["status"], "parsed")
        self.assertEqual(parsed["pattern"], "S-P-O")
        self.assertEqual(parsed["roles"]["subject"], ["anak"])
        self.assertEqual(parsed["roles"]["predicate"], ["makan"])
        self.assertEqual(parsed["roles"]["object"], ["nasi"])

    def test_simple_sentence_parser_uses_real_dictionary_pipeline(self):
        result = self.analyze("Aku sedang bekerja di rumah.")
        parsed = parse_sentence(result)
        self.assertEqual(parsed["status"], "parsed")
        self.assertEqual(parsed["pattern"], "S-P-K")
        self.assertEqual(parsed["roles"]["subject"], ["aku"])
        self.assertEqual(parsed["roles"]["predicate"], ["sedang", "bekerja"])
        self.assertEqual(
            parsed["roles"]["adjuncts"],
            [{"preposition": "di", "phrase": ["rumah"]}],
        )

    def test_fronted_prepositional_adjunct_uses_real_dictionary_pipeline(self):
        result = parse_sentence(self.analyze("Di rumah aku bekerja."))
        self.assertEqual(result["status"], "parsed")
        self.assertEqual(result["pattern"], "S-P-K")
        self.assertEqual(result["roles"]["subject"], ["aku"])
        self.assertEqual(result["roles"]["predicate"], ["bekerja"])
        self.assertEqual(
            result["roles"]["adjuncts"],
            [{"preposition": "di", "phrase": ["rumah"]}],
        )

    def test_valency_guided_postverbal_subject_uses_real_dictionary_pipeline(self):
        analyzed = self.analyze("Muncul masalah.")
        verb = self.token(analyzed, "muncul")
        self.assertEqual(verb["pos"], ["VERB"])
        self.assertEqual(verb["candidates"][0]["entry"]["senses"][0]["valency_frames"][0]["arguments"], [{
            "argument_id": "A1",
            "syntactic_role": "SUBJ",
            "semantic_role": "THEME",
            "required": True,
            "realizations": [{"type": "NP"}],
        }])
        parsed = parse_sentence(analyzed)
        self.assertEqual(parsed["status"], "parsed")
        self.assertEqual(parsed["pattern"], "P-S")
        self.assertEqual(parsed["roles"]["subject"], ["masalah"])
        self.assertEqual(parsed["roles"]["predicate"], ["muncul"])
        self.assertEqual(parsed["roles"]["object"], [])

        fronted = parse_sentence(self.analyze("Di rumah muncul masalah."))
        self.assertEqual(fronted["status"], "parsed")
        self.assertEqual(fronted["pattern"], "K-P-S")
        self.assertEqual(fronted["roles"]["subject"], ["masalah"])
        self.assertEqual(fronted["roles"]["predicate"], ["muncul"])
        self.assertEqual(fronted["roles"]["adjuncts"], [
            {"preposition": "di", "phrase": ["rumah"]}
        ])

    def test_valency_guided_inversion_keeps_postverbal_nominal_modifier(self):
        for sentence, expected_pattern, expected_adjuncts in (
            ("Muncul masalah besar.", "P-S", []),
            (
                "Di rumah muncul masalah besar.",
                "K-P-S",
                [{"preposition": "di", "phrase": ["rumah"]}],
            ),
        ):
            with self.subTest(sentence=sentence):
                parsed = parse_sentence(self.analyze(sentence))
                self.assertEqual(parsed["status"], "parsed")
                self.assertEqual(parsed["pattern"], expected_pattern)
                self.assertEqual(parsed["roles"]["subject"], ["masalah", "besar"])
                self.assertEqual(parsed["roles"]["predicate"], ["muncul"])
                self.assertEqual(parsed["roles"]["object"], [])
                self.assertEqual(parsed["roles"]["adjuncts"], expected_adjuncts)

    def test_postverbal_noun_without_unique_valency_remains_unresolved_in_real_pipeline(self):
        analyzed = self.analyze("Timbul masalah.")
        verb = self.token(analyzed, "timbul")
        noun = self.token(analyzed, "masalah")
        self.assertEqual(verb["pos"], ["VERB"])
        self.assertEqual(noun["pos"], ["NOUN"])
        parsed = parse_sentence(analyzed)
        self.assertEqual(parsed["status"], "unresolved")
        self.assertIsNone(parsed["pattern"])
        self.assertEqual(parsed["roles"]["subject"], [])
        self.assertEqual(parsed["roles"]["predicate"], ["timbul"])
        self.assertEqual(parsed["roles"]["object"], [])
        self.assertEqual(parsed["unresolved_tokens"], ["masalah"])

    def test_kps_candidate_and_omitted_subject_object_remain_unresolved_in_real_pipeline(self):
        cases = (
            ("Di rumah terdengar suara.", "terdengar", "suara"),
            ("Di rumah membaca buku.", "membaca", "buku"),
        )
        for sentence, predicate, nominal in cases:
            with self.subTest(sentence=sentence):
                parsed = parse_sentence(self.analyze(sentence))
                self.assertEqual(parsed["status"], "unresolved")
                self.assertIsNone(parsed["pattern"])
                self.assertEqual(parsed["roles"]["subject"], [])
                self.assertEqual(parsed["roles"]["predicate"], [predicate])
                self.assertEqual(parsed["roles"]["object"], [])
                self.assertEqual(parsed["unresolved_tokens"], [nominal])
                self.assertEqual(
                    parsed["roles"]["adjuncts"],
                    [{"preposition": "di", "phrase": ["rumah"]}],
                )

    def test_fronted_prepositional_phrase_is_not_misread_in_real_dictionary_pipeline(self):
        parsed = parse_sentence(self.analyze("Di rumah terdengar suara."))
        self.assertEqual(parsed["status"], "unresolved")
        self.assertIsNone(parsed["pattern"])
        self.assertEqual(parsed["roles"]["subject"], [])
        self.assertEqual(parsed["roles"]["predicate"], ["terdengar"])
        self.assertEqual(parsed["roles"]["object"], [])
        self.assertEqual(
            parsed["roles"]["adjuncts"],
            [{"preposition": "di", "phrase": ["rumah"]}],
        )
        self.assertEqual(parsed["unresolved_tokens"], ["suara"])

    def test_terdengar_is_verb_from_explicit_derived_form_annotation(self):
        # This test covers lexical POS only. K-P-S parsing remains a separate
        # parser task and must not be conflated with derived-form recognition.
        analyzed = self.analyze("Di rumah terdengar suara.")
        token = self.token(analyzed, "terdengar")
        self.assertEqual(token["status"], "matched")
        self.assertEqual(token["pos"], ["VERB"])
        self.assertEqual(token["pos_source"], "dictionary")
        self.assertEqual(token["pos_status"], "identified")
        self.assertTrue(
            any(candidate["lemma"] == "dengar" for candidate in token["candidates"])
        )

    def test_fronted_temporal_adverb_with_modal_uses_real_dictionary_pipeline(self):
        parsed = parse_sentence(self.analyze("Besok aku akan makan nasi."))
        self.assertEqual(parsed["status"], "parsed")
        self.assertEqual(parsed["pattern"], "S-P-O-K")
        self.assertEqual(parsed["roles"]["subject"], ["aku"])
        self.assertEqual(parsed["roles"]["predicate"], ["akan", "makan"])
        self.assertEqual(parsed["roles"]["object"], ["nasi"])
        self.assertEqual(
            parsed["roles"]["adjuncts"],
            [{"adverb": "besok", "kind": "temporal"}],
        )

    def test_postposed_temporal_adverb_uses_real_dictionary_pipeline(self):
        intransitive = parse_sentence(self.analyze("Aku bekerja besok."))
        self.assertEqual(intransitive["status"], "parsed")
        self.assertEqual(intransitive["pattern"], "S-P-K")
        self.assertEqual(intransitive["roles"]["subject"], ["aku"])
        self.assertEqual(intransitive["roles"]["predicate"], ["bekerja"])
        self.assertEqual(
            intransitive["roles"]["adjuncts"],
            [{"adverb": "besok", "kind": "temporal"}],
        )

        transitive = parse_sentence(self.analyze("Aku makan nasi nanti."))
        self.assertEqual(transitive["status"], "parsed")
        self.assertEqual(transitive["pattern"], "S-P-O-K")
        self.assertEqual(transitive["roles"]["object"], ["nasi"])
        self.assertEqual(
            transitive["roles"]["adjuncts"],
            [{"adverb": "nanti", "kind": "temporal"}],
        )

    def test_multiple_fronted_adjuncts_use_real_dictionary_pipeline(self):
        parsed = parse_sentence(self.analyze("Di rumah pada malam hari aku bekerja."))
        self.assertEqual(parsed["status"], "parsed")
        self.assertEqual(parsed["pattern"], "S-P-K")
        self.assertEqual(parsed["roles"]["subject"], ["aku"])
        self.assertEqual(parsed["roles"]["predicate"], ["bekerja"])
        self.assertEqual(parsed["roles"]["adjuncts"], [
            {"preposition": "di", "phrase": ["rumah"]},
            {"preposition": "pada", "phrase": ["malam", "hari"]},
        ])

    def test_three_coordinated_clauses_use_real_dictionary_pipeline(self):
        parsed = parse_sentence(self.analyze("Aku bekerja dan dia makan dan mereka belajar."))
        self.assertEqual(parsed["status"], "parsed")
        self.assertEqual(parsed["pattern"], "KLAUSA-KOORDINATIF")
        self.assertEqual(len(parsed["clauses"]), 3)
        self.assertEqual(
            [clause["connector"] for clause in parsed["clauses"]],
            [None, "dan", "dan"],
        )
        self.assertEqual(
            [clause["analysis"]["roles"]["subject"] for clause in parsed["clauses"]],
            [["aku"], ["dia"], ["mereka"]],
        )
        self.assertEqual(
            [clause["analysis"]["roles"]["predicate"] for clause in parsed["clauses"]],
            [["bekerja"], ["makan"], ["belajar"]],
        )

    def test_fronted_causal_subordinate_uses_real_dictionary_pipeline(self):
        parsed = parse_sentence(self.analyze("Karena dia makan, aku pulang."))
        self.assertEqual(parsed["status"], "parsed")
        self.assertEqual(parsed["pattern"], "KLAUSA-SUBORDINATIF")
        self.assertEqual(parsed["clauses"][0]["subordinator"], "karena")
        self.assertEqual(parsed["clauses"][0]["relation_to_next"], "sebab")
        self.assertEqual(parsed["clauses"][1]["analysis"]["roles"]["subject"], ["aku"])

    def test_fronted_causal_subordinate_with_sebab_uses_real_pipeline(self):
        parsed = parse_sentence(self.analyze("Sebab hujan turun, aku pulang."))
        self.assertEqual(parsed["status"], "parsed")
        self.assertEqual(parsed["pattern"], "KLAUSA-SUBORDINATIF")
        self.assertEqual(len(parsed["clauses"]), 2)
        subordinate, main_clause = parsed["clauses"]
        self.assertEqual(subordinate["subordinator"], "sebab")
        self.assertEqual(subordinate["relation_to_next"], "sebab")
        self.assertEqual(subordinate["analysis"]["pattern"], "S-P")
        self.assertEqual(subordinate["analysis"]["roles"]["subject"], ["hujan"])
        self.assertEqual(subordinate["analysis"]["roles"]["predicate"], ["turun"])
        self.assertEqual(main_clause["analysis"]["pattern"], "S-P")
        self.assertEqual(main_clause["analysis"]["roles"]["subject"], ["aku"])
        self.assertEqual(main_clause["analysis"]["roles"]["predicate"], ["pulang"])

    def test_fronted_temporal_subordinate_uses_real_dictionary_pipeline(self):
        parsed = parse_sentence(self.analyze("Ketika dia makan, aku pulang."))
        self.assertEqual(parsed["status"], "parsed")
        self.assertEqual(parsed["pattern"], "KLAUSA-SUBORDINATIF")
        self.assertEqual(parsed["clauses"][0]["subordinator"], "ketika")
        self.assertEqual(parsed["clauses"][0]["relation_to_next"], "temporal")
        self.assertEqual(parsed["clauses"][1]["analysis"]["roles"]["predicate"], ["pulang"])

    def test_contrastive_clauses_use_real_dictionary_pipeline(self):
        parsed = parse_sentence(self.analyze("Aku bekerja namun dia makan."))
        self.assertEqual(parsed["status"], "parsed")
        self.assertEqual(parsed["pattern"], "KLAUSA-KOORDINATIF")
        self.assertEqual(parsed["clauses"][1]["connector"], "namun")
        self.assertEqual(
            parsed["clauses"][1]["relation_to_previous"], "pertentangan"
        )

    def test_two_coordinated_clauses_use_real_dictionary_pipeline(self):
        parsed = parse_sentence(self.analyze("Aku bekerja dan dia makan."))
        self.assertEqual(parsed["status"], "parsed")
        self.assertEqual(parsed["pattern"], "KLAUSA-KOORDINATIF")
        self.assertEqual(len(parsed["clauses"]), 2)
        first = parsed["clauses"][0]["analysis"]
        second = parsed["clauses"][1]["analysis"]
        self.assertEqual(first["roles"]["subject"], ["aku"])
        self.assertEqual(first["roles"]["predicate"], ["bekerja"])
        self.assertEqual(parsed["clauses"][1]["connector"], "dan")
        self.assertEqual(second["roles"]["subject"], ["dia"])
        self.assertEqual(second["roles"]["predicate"], ["makan"])

    def test_coordinated_subject_and_object_use_real_dictionary_pipeline(self):
        parsed = parse_sentence(self.analyze("Aku dan dia membeli nasi dan roti."))
        self.assertEqual(parsed["status"], "parsed")
        self.assertEqual(parsed["pattern"], "S-P-O")
        self.assertEqual(parsed["roles"]["subject"], ["aku", "dan", "dia"])
        self.assertEqual(parsed["roles"]["predicate"], ["membeli"])
        self.assertEqual(parsed["roles"]["object"], ["nasi", "dan", "roti"])

    def test_verbal_negation_parses_through_real_dictionary_pipeline(self):
        result = parse_sentence(self.analyze("Kami tidak membeli ikan."))
        self.assertEqual(result["status"], "parsed")
        self.assertEqual(result["pattern"], "S-P-O")
        self.assertEqual(result["roles"]["subject"], ["kami"])
        self.assertEqual(result["roles"]["predicate"], ["tidak", "membeli"])
        self.assertEqual(result["roles"]["object"], ["ikan"])


    def test_adjectival_nonverbal_predicate_uses_real_dictionary_pipeline(self):
        result = parse_sentence(self.analyze("Dia sakit."))
        self.assertEqual(result["status"], "parsed")
        self.assertEqual(result["pattern"], "S-P")
        self.assertEqual(result["roles"]["subject"], ["Dia".lower()])
        self.assertEqual(result["roles"]["predicate"], ["sakit"])

    def test_demonstrative_subject_nonverbal_predicate_uses_real_pipeline(self):
        result = self.analyze("Rumah itu besar.")
        self.assertEqual(self.token(result, "rumah")["pos"], ["NOUN"])
        self.assertEqual(self.token(result, "itu")["pos"], ["PRON"])
        self.assertEqual(self.token(result, "besar")["pos"], ["ADJ"])
        parsed = parse_sentence(result)
        self.assertEqual(parsed["status"], "parsed")
        self.assertEqual(parsed["pattern"], "S-P")
        self.assertEqual(parsed["roles"]["subject"], ["rumah", "itu"])
        self.assertEqual(parsed["roles"]["predicate"], ["besar"])

    def test_uncovered_linking_verb_becomes_unknown_and_parser_abstains(self):
        result = self.analyze("Dia menjadi dokter.")
        verb = self.token(result, "menjadi")
        self.assertEqual(verb["status"], "unknown")
        self.assertEqual(verb["pos"], [])
        parsed = parse_sentence(result)
        self.assertEqual(parsed["status"], "unresolved")
        self.assertEqual(parsed["roles"]["complement"], [])

    def test_uncovered_adjectival_complement_is_not_guessed(self):
        result = self.analyze("Mereka tampak bahagia.")
        linking_verb = self.token(result, "tampak")
        adjective = self.token(result, "bahagia")
        self.assertEqual(linking_verb["status"], "matched")
        self.assertEqual(linking_verb["pos"], ["VERB"])
        self.assertEqual(linking_verb["pos_source"], "dictionary")
        self.assertEqual(adjective["status"], "unknown")
        parsed = parse_sentence(result)
        self.assertEqual(parsed["status"], "partial")
        self.assertEqual(parsed["roles"]["predicate"], ["tampak"])
        self.assertEqual(parsed["roles"]["complement"], [])
        self.assertEqual(parsed["unresolved_tokens"], ["bahagia"])

    def test_postposed_temporal_subordinate_uses_real_dictionary_pipeline(self):
        analyzed = self.analyze("Aku pulang ketika hujan turun.")
        parsed = parse_sentence(analyzed)
        self.assertEqual(parsed["status"], "parsed")
        self.assertEqual(parsed["pattern"], "KLAUSA-SUBORDINATIF")
        self.assertEqual(len(parsed["clauses"]), 2)
        main_clause, subordinate = parsed["clauses"]
        self.assertEqual(main_clause["analysis"]["pattern"], "S-P")
        self.assertEqual(main_clause["analysis"]["roles"]["subject"], ["aku"])
        self.assertEqual(main_clause["analysis"]["roles"]["predicate"], ["pulang"])
        self.assertEqual(subordinate["subordinator"], "ketika")
        self.assertEqual(subordinate["relation_to_previous"], "temporal")
        self.assertEqual(subordinate["analysis"]["pattern"], "S-P")
        self.assertEqual(subordinate["analysis"]["roles"]["subject"], ["hujan"])
        self.assertEqual(subordinate["analysis"]["roles"]["predicate"], ["turun"])

    def test_negated_main_clause_with_postposed_temporal_subordinate_uses_real_pipeline(self):
        analyzed = self.analyze("Aku tidak pulang ketika hujan turun.")
        parsed = parse_sentence(analyzed)
        self.assertEqual(parsed["status"], "parsed")
        self.assertEqual(parsed["pattern"], "KLAUSA-SUBORDINATIF")
        self.assertEqual(len(parsed["clauses"]), 2)
        main_clause, subordinate = parsed["clauses"]
        self.assertEqual(main_clause["analysis"]["pattern"], "S-P")
        self.assertEqual(main_clause["analysis"]["roles"]["subject"], ["aku"])
        self.assertEqual(main_clause["analysis"]["roles"]["predicate"], ["tidak", "pulang"])
        self.assertEqual(
            main_clause["analysis"]["predicate_structure"]["modifiers"],
            [{"token": "tidak", "kind": "negation"}],
        )
        self.assertEqual(subordinate["subordinator"], "ketika")
        self.assertEqual(subordinate["relation_to_previous"], "temporal")
        self.assertEqual(subordinate["analysis"]["pattern"], "S-P")
        self.assertEqual(subordinate["analysis"]["roles"]["subject"], ["hujan"])
        self.assertEqual(subordinate["analysis"]["roles"]["predicate"], ["turun"])

    def test_negated_main_clause_with_postposed_causal_subordinate_uses_real_pipeline(self):
        analyzed = self.analyze("Aku tidak pulang karena hujan turun.")
        parsed = parse_sentence(analyzed)
        self.assertEqual(parsed["status"], "parsed")
        self.assertEqual(parsed["pattern"], "KLAUSA-SUBORDINATIF")
        self.assertEqual(len(parsed["clauses"]), 2)
        main_clause, subordinate = parsed["clauses"]
        self.assertEqual(main_clause["analysis"]["pattern"], "S-P")
        self.assertEqual(main_clause["analysis"]["roles"]["subject"], ["aku"])
        self.assertEqual(main_clause["analysis"]["roles"]["predicate"], ["tidak", "pulang"])
        self.assertEqual(
            main_clause["analysis"]["predicate_structure"]["modifiers"],
            [{"token": "tidak", "kind": "negation"}],
        )
        self.assertEqual(subordinate["subordinator"], "karena")
        self.assertEqual(subordinate["relation_to_previous"], "sebab")
        self.assertEqual(subordinate["analysis"]["pattern"], "S-P")
        self.assertEqual(subordinate["analysis"]["roles"]["subject"], ["hujan"])
        self.assertEqual(subordinate["analysis"]["roles"]["predicate"], ["turun"])

    def test_postposed_causal_subordinate_with_sebab_uses_real_pipeline(self):
        analyzed = self.analyze("Aku pulang sebab hujan turun.")
        parsed = parse_sentence(analyzed)
        self.assertEqual(parsed["status"], "parsed")
        self.assertEqual(parsed["pattern"], "KLAUSA-SUBORDINATIF")
        self.assertEqual(len(parsed["clauses"]), 2)
        main_clause, subordinate = parsed["clauses"]
        self.assertEqual(main_clause["analysis"]["pattern"], "S-P")
        self.assertEqual(main_clause["analysis"]["roles"]["subject"], ["aku"])
        self.assertEqual(main_clause["analysis"]["roles"]["predicate"], ["pulang"])
        self.assertEqual(subordinate["subordinator"], "sebab")
        self.assertEqual(subordinate["relation_to_previous"], "sebab")
        self.assertEqual(subordinate["analysis"]["pattern"], "S-P")
        self.assertEqual(subordinate["analysis"]["roles"]["subject"], ["hujan"])
        self.assertEqual(subordinate["analysis"]["roles"]["predicate"], ["turun"])

    def test_postposed_causal_subordinate_uses_real_dictionary(self):
        result = self.analyze("Aku pulang karena hujan turun.")
        parsed = parse_sentence(result)
        self.assertEqual(parsed["status"], "parsed")
        self.assertEqual(parsed["pattern"], "KLAUSA-SUBORDINATIF")
        self.assertEqual(parsed["clauses"][0]["analysis"]["roles"]["subject"], ["aku"])
        self.assertEqual(parsed["clauses"][1]["subordinator"], "karena")
        self.assertEqual(parsed["clauses"][1]["analysis"]["roles"]["subject"], ["hujan"])
        self.assertEqual(parsed["clauses"][1]["analysis"]["roles"]["predicate"], ["turun"])

    def test_fronted_elliptical_concessive_adjective_uses_real_dictionary(self):
        result = self.analyze("Walaupun lelah, dia bekerja.")
        adjective = self.token(result, "lelah")
        self.assertEqual(adjective["status"], "matched")
        self.assertEqual(adjective["pos"], ["ADJ"])
        parsed = parse_sentence(result)
        self.assertEqual(parsed["status"], "partial")
        self.assertEqual(parsed["pattern"], "KLAUSA-SUBORDINATIF")
        subordinate = parsed["clauses"][0]["analysis"]
        self.assertEqual(subordinate["pattern"], "P-ELIPTIS")
        self.assertEqual(subordinate["roles"]["subject"], [])
        self.assertEqual(subordinate["roles"]["predicate"], ["lelah"])
        self.assertEqual(parsed["clauses"][1]["analysis"]["roles"]["subject"], ["dia"])

    def test_postposed_full_concessive_clause_with_meskipun_uses_real_pipeline(self):
        analyzed = self.analyze("Aku pergi meskipun hujan turun.")
        parsed = parse_sentence(analyzed)
        self.assertEqual(parsed["status"], "parsed")
        self.assertEqual(parsed["pattern"], "KLAUSA-SUBORDINATIF")
        self.assertEqual(len(parsed["clauses"]), 2)
        main_clause, subordinate = parsed["clauses"]
        self.assertEqual(main_clause["analysis"]["pattern"], "S-P")
        self.assertEqual(main_clause["analysis"]["roles"]["subject"], ["aku"])
        self.assertEqual(main_clause["analysis"]["roles"]["predicate"], ["pergi"])
        self.assertEqual(subordinate["subordinator"], "meskipun")
        self.assertEqual(subordinate["relation_to_previous"], "konsesi")
        self.assertEqual(subordinate["analysis"]["pattern"], "S-P")
        self.assertEqual(subordinate["analysis"]["roles"]["subject"], ["hujan"])
        self.assertEqual(subordinate["analysis"]["roles"]["predicate"], ["turun"])

    def test_fronted_full_concessive_clause_with_meskipun_uses_real_pipeline(self):
        analyzed = self.analyze("Meskipun hujan turun, aku pergi.")
        parsed = parse_sentence(analyzed)
        self.assertEqual(parsed["status"], "parsed")
        self.assertEqual(parsed["pattern"], "KLAUSA-SUBORDINATIF")
        self.assertEqual(len(parsed["clauses"]), 2)
        subordinate, main_clause = parsed["clauses"]
        self.assertEqual(subordinate["subordinator"], "meskipun")
        self.assertEqual(subordinate["relation_to_next"], "konsesi")
        self.assertEqual(subordinate["analysis"]["pattern"], "S-P")
        self.assertEqual(subordinate["analysis"]["roles"]["subject"], ["hujan"])
        self.assertEqual(subordinate["analysis"]["roles"]["predicate"], ["turun"])
        self.assertIsNone(main_clause["subordinator"])
        self.assertEqual(main_clause["relation_to_previous"], "konsesi")
        self.assertEqual(main_clause["analysis"]["pattern"], "S-P")
        self.assertEqual(main_clause["analysis"]["roles"]["subject"], ["aku"])
        self.assertEqual(main_clause["analysis"]["roles"]["predicate"], ["pergi"])

    def test_fronted_elliptical_concessive_with_meskipun_uses_real_pipeline(self):
        result = self.analyze("Meskipun lelah, aku pergi.")
        expected = {
            "meskipun": "CONJ",
            "lelah": "ADJ",
            "aku": "PRON",
            "pergi": "VERB",
        }
        for surface, pos in expected.items():
            with self.subTest(surface=surface):
                token = self.token(result, surface)
                self.assertEqual(token["status"], "matched")
                self.assertEqual(token["pos"], [pos])
                self.assertEqual(token["pos_source"], "dictionary")
                self.assertEqual(token["pos_status"], "identified")

        parsed = parse_sentence(result)
        self.assertEqual(parsed["status"], "partial")
        self.assertEqual(parsed["pattern"], "KLAUSA-SUBORDINATIF")
        subordinate, main_clause = parsed["clauses"]
        self.assertEqual(subordinate["subordinator"], "meskipun")
        self.assertEqual(subordinate["relation_to_next"], "konsesi")
        self.assertEqual(subordinate["analysis"]["pattern"], "P-ELIPTIS")
        self.assertEqual(subordinate["analysis"]["roles"]["subject"], [])
        self.assertEqual(subordinate["analysis"]["roles"]["predicate"], ["lelah"])
        self.assertEqual(main_clause["analysis"]["pattern"], "S-P")
        self.assertEqual(main_clause["analysis"]["roles"]["subject"], ["aku"])
        self.assertEqual(main_clause["analysis"]["roles"]["predicate"], ["pergi"])
    def test_personal_pronouns_use_real_dictionary_pipeline_as_subject_and_object(self):
        pronouns = ("aku", "saya", "kamu", "engkau", "dia", "mereka", "kita", "kami", "kalian", "anda", "beliau", "ia", "kau")

        for pronoun in pronouns:
            with self.subTest(role="subject", pronoun=pronoun):
                analyzed = self.analyze(f"{pronoun} makan nasi.")
                token = self.token(analyzed, pronoun)
                self.assertEqual(token["status"], "matched")
                self.assertEqual(token["pos"], ["PRON"])
                self.assertEqual(token["pos_source"], "dictionary")
                self.assertEqual(token["pos_status"], "identified")

                parsed = parse_sentence(analyzed)
                self.assertEqual(parsed["status"], "parsed")
                self.assertEqual(parsed["pattern"], "S-P-O")
                self.assertEqual(parsed["roles"]["subject"], [pronoun])
                self.assertEqual(parsed["roles"]["predicate"], ["makan"])
                self.assertEqual(parsed["roles"]["object"], ["nasi"])

            with self.subTest(role="object", pronoun=pronoun):
                analyzed = self.analyze(f"Dia lihat {pronoun}.")
                token = self.token(analyzed, pronoun)
                self.assertEqual(token["status"], "matched")
                self.assertEqual(token["pos"], ["PRON"])
                self.assertEqual(token["pos_source"], "dictionary")
                self.assertEqual(token["pos_status"], "identified")

                parsed = parse_sentence(analyzed)
                self.assertEqual(parsed["status"], "parsed")
                self.assertEqual(parsed["pattern"], "S-P-O")
                self.assertEqual(parsed["roles"]["subject"], ["dia"])
                self.assertEqual(parsed["roles"]["predicate"], ["lihat"])
                self.assertEqual(parsed["roles"]["object"], [pronoun])


    def test_informal_personal_pronouns_use_real_dictionary_pipeline_as_subject_and_object(self):
        pronouns = ("gue", "gua", "gw", "lu", "lo", "elu")

        for pronoun in pronouns:
            with self.subTest(role="subject", pronoun=pronoun):
                analyzed = self.analyze(f"{pronoun} makan nasi.")
                token = self.token(analyzed, pronoun)
                self.assertEqual(token["status"], "matched")
                self.assertEqual(token["pos"], ["PRON"])
                self.assertEqual(token["pos_source"], "dictionary")
                self.assertEqual(token["pos_status"], "identified")

                parsed = parse_sentence(analyzed)
                self.assertEqual(parsed["status"], "parsed")
                self.assertEqual(parsed["pattern"], "S-P-O")
                self.assertEqual(parsed["roles"]["subject"], [pronoun])
                self.assertEqual(parsed["roles"]["predicate"], ["makan"])
                self.assertEqual(parsed["roles"]["object"], ["nasi"])

            with self.subTest(role="object", pronoun=pronoun):
                analyzed = self.analyze(f"Dia lihat {pronoun}.")
                token = self.token(analyzed, pronoun)
                self.assertEqual(token["status"], "matched")
                self.assertEqual(token["pos"], ["PRON"])
                self.assertEqual(token["pos_source"], "dictionary")
                self.assertEqual(token["pos_status"], "identified")

                parsed = parse_sentence(analyzed)
                self.assertEqual(parsed["status"], "parsed")
                self.assertEqual(parsed["pattern"], "S-P-O")
                self.assertEqual(parsed["roles"]["subject"], ["dia"])
                self.assertEqual(parsed["roles"]["predicate"], ["lihat"])
                self.assertEqual(parsed["roles"]["object"], [pronoun])

    def test_fronted_prepositional_adjunct_keeps_explicit_pronoun_subject_in_real_pipeline(self):
        analyzed = self.analyze("Dari rumah dia bekerja.")

        expected = {
            "dari": "PREP",
            "rumah": "NOUN",
            "dia": "PRON",
            "bekerja": "VERB",
        }
        for surface, pos in expected.items():
            with self.subTest(surface=surface):
                token = self.token(analyzed, surface)
                self.assertEqual(token["status"], "matched")
                self.assertEqual(token["pos"], [pos])
                self.assertEqual(token["pos_source"], "dictionary")
                self.assertEqual(token["pos_status"], "identified")

        parsed = parse_sentence(analyzed)
        self.assertEqual(parsed["status"], "parsed")
        self.assertEqual(parsed["pattern"], "S-P-K")
        self.assertEqual(parsed["roles"]["subject"], ["dia"])
        self.assertEqual(parsed["roles"]["predicate"], ["bekerja"])
        self.assertEqual(
            parsed["roles"]["adjuncts"],
            [{"preposition": "dari", "phrase": ["rumah"]}],
        )
        self.assertEqual(parsed["unresolved_tokens"], [])

    def test_derived_nominal_with_nya_clitic_is_recognized_in_real_pipeline(self):
        analyzed = self.analyze("perasaannya")
        bound = self.token(analyzed, "perasaannya")

        self.assertEqual(bound["status"], "unknown")
        self.assertEqual(len(bound["morphology_candidates"]), 1)
        candidate = bound["morphology_candidates"][0]
        self.assertEqual(candidate["base_form"], "perasaan")
        self.assertEqual(candidate["rule"], "clitic_nya")
        self.assertEqual(candidate["clitic"], "nya")
        self.assertTrue(
            any(
                item["lemma"] == "rasa"
                and item["match_type"] == "derived_form"
                for item in candidate["candidates"]
            )
        )

    def test_derived_nominal_with_mu_clitic_is_recognized_in_real_pipeline(self):
        analyzed = self.analyze("perasaanmu")
        bound = self.token(analyzed, "perasaanmu")

        self.assertEqual(bound["status"], "unknown")
        self.assertEqual(len(bound["morphology_candidates"]), 1)
        candidate = bound["morphology_candidates"][0]
        self.assertEqual(candidate["base_form"], "perasaan")
        self.assertEqual(candidate["rule"], "clitic_mu")
        self.assertEqual(candidate["clitic"], "mu")
        self.assertTrue(
            any(
                item["lemma"] == "rasa"
                and item["match_type"] == "derived_form"
                for item in candidate["candidates"]
            )
        )

    def test_derived_nominal_with_ku_clitic_is_recognized_in_real_pipeline(self):
        analyzed = self.analyze("perasaanku")
        bound = self.token(analyzed, "perasaanku")

        self.assertEqual(bound["status"], "unknown")
        self.assertEqual(len(bound["morphology_candidates"]), 1)
        candidate = bound["morphology_candidates"][0]
        self.assertEqual(candidate["base_form"], "perasaan")
        self.assertEqual(candidate["rule"], "clitic_ku")
        self.assertEqual(candidate["clitic"], "ku")
        self.assertTrue(
            any(
                item["lemma"] == "rasa"
                and item["match_type"] == "derived_form"
                for item in candidate["candidates"]
            )
        )

    def test_multi_affix_verb_with_nya_clitic_is_recognized_in_real_pipeline(self):
        analyzed = self.analyze("memilikinya")
        bound = self.token(analyzed, "memilikinya")

        self.assertEqual(bound["status"], "unknown")
        self.assertEqual(len(bound["morphology_candidates"]), 1)
        candidate = bound["morphology_candidates"][0]
        self.assertEqual(candidate["base_form"], "memiliki")
        self.assertEqual(candidate["rule"], "clitic_nya")
        self.assertEqual(candidate["clitic"], "nya")
        self.assertTrue(
            any(
                item["lemma"] == "milik"
                and item["match_type"] == "derived_form"
                for item in candidate["candidates"]
            )
        )

    def test_multi_affix_verb_with_ku_clitic_is_recognized_in_real_pipeline(self):
        analyzed = self.analyze("memilikiku")
        bound = self.token(analyzed, "memilikiku")

        self.assertEqual(bound["status"], "unknown")
        self.assertEqual(len(bound["morphology_candidates"]), 1)
        candidate = bound["morphology_candidates"][0]
        self.assertEqual(candidate["base_form"], "memiliki")
        self.assertEqual(candidate["rule"], "clitic_ku")
        self.assertEqual(candidate["clitic"], "ku")
        self.assertTrue(
            any(
                item["lemma"] == "milik"
                and item["match_type"] == "derived_form"
                for item in candidate["candidates"]
            )
        )


    def test_multi_affix_verb_with_mu_clitic_is_recognized_in_real_pipeline(self):
        analyzed = self.analyze("memilikimu")
        bound = self.token(analyzed, "memilikimu")

        self.assertEqual(bound["status"], "unknown")
        self.assertEqual(len(bound["morphology_candidates"]), 1)
        candidate = bound["morphology_candidates"][0]
        self.assertEqual(candidate["base_form"], "memiliki")
        self.assertEqual(candidate["rule"], "clitic_mu")
        self.assertEqual(candidate["clitic"], "mu")
        self.assertTrue(
            any(
                item["lemma"] == "milik"
                and item["match_type"] == "derived_form"
                for item in candidate["candidates"]
            )
        )


    def test_bound_pronoun_clitics_are_exposed_by_real_lexical_pipeline(self):
        cases = {
            "bukuku": ("buku", "ku"),
            "rumahmu": ("rumah", "mu"),
            "bukunya": ("buku", "nya"),
            "lihatku": ("lihat", "ku"),
            "lihatmu": ("lihat", "mu"),
            "lihatnya": ("lihat", "nya"),
        }
        for surface, (base, clitic) in cases.items():
            with self.subTest(surface=surface):
                result = self.analyze(surface)
                token = self.token(result, surface)
                self.assertEqual(token["kind"], "word")
                self.assertEqual(token["status"], "unknown")
                self.assertEqual(len(token["morphology_candidates"]), 1)
                candidate = token["morphology_candidates"][0]
                self.assertEqual(candidate["base_form"], base)
                self.assertEqual(candidate["clitic"], clitic)
                self.assertEqual(candidate["interpretations"], ["possessive", "object"])
                components = token["clitic_pos_candidates"]
                self.assertEqual(len(components), 1)
                self.assertEqual(components[0]["clitic"], clitic)
                self.assertEqual(components[0]["clitic_pos"], ["PRON"])
                self.assertEqual(components[0]["function_candidates"], ["possessive", "object"])
                self.assertEqual(components[0]["function_status"], "unresolved")
                self.assertEqual(token["pos"], [])
                self.assertEqual(token["pos_status"], "unknown")

    def test_nominal_bound_clitic_is_parsed_as_possessive_object_phrase_in_real_pipeline(self):
        analyzed = self.analyze("Dia lihat bukuku.")
        bound = self.token(analyzed, "bukuku")
        self.assertEqual(bound["status"], "unknown")
        self.assertEqual(bound["pos"], [])
        self.assertEqual(bound["clitic_pos_candidates"][0]["host_pos"], ["NOUN"])
        parsed = parse_sentence(analyzed)
        self.assertEqual(parsed["status"], "parsed")
        self.assertEqual(parsed["pattern"], "S-P-O")
        self.assertEqual(parsed["roles"]["subject"], ["dia"])
        self.assertEqual(parsed["roles"]["predicate"], ["lihat"])
        self.assertEqual(parsed["roles"]["object"], ["bukuku"])
        self.assertEqual(parsed["clitic_analysis"], [{
            "surface": "bukuku",
            "base_form": "buku",
            "clitic": "ku",
            "function": "possessive",
            "function_status": "selected_by_host_pos",
            "nominal_phrase_role": "object",
        }])

    def test_nominal_possessive_clitic_can_head_subject_phrase_in_real_pipeline(self):
        analyzed = self.analyze("Bukuku jatuh.")
        bound = self.token(analyzed, "bukuku")
        self.assertEqual(bound["clitic_pos_candidates"][0]["host_pos"], ["NOUN"])
        parsed = parse_sentence(analyzed)
        self.assertEqual(parsed["status"], "parsed")
        self.assertEqual(parsed["pattern"], "S-P")
        self.assertEqual(parsed["roles"]["subject"], ["bukuku"])
        self.assertEqual(parsed["roles"]["predicate"], ["jatuh"])
        self.assertEqual(parsed["clitic_analysis"], [{
            "surface": "bukuku",
            "base_form": "buku",
            "clitic": "ku",
            "function": "possessive",
            "function_status": "selected_by_host_pos",
            "nominal_phrase_role": "subject",
        }])

    def test_nominal_mu_clitic_can_head_subject_phrase_in_real_pipeline(self):
        analyzed = self.analyze("Bukumu jatuh.")
        bound = self.token(analyzed, "bukumu")
        self.assertEqual(bound["clitic_pos_candidates"][0]["host_pos"], ["NOUN"])
        parsed = parse_sentence(analyzed)
        self.assertEqual(parsed["status"], "parsed")
        self.assertEqual(parsed["pattern"], "S-P")
        self.assertEqual(parsed["roles"]["subject"], ["bukumu"])
        self.assertEqual(parsed["roles"]["predicate"], ["jatuh"])
        self.assertEqual(parsed["clitic_analysis"], [{
            "surface": "bukumu",
            "base_form": "buku",
            "clitic": "mu",
            "function": "possessive",
            "function_status": "selected_by_host_pos",
            "nominal_phrase_role": "subject",
        }])

    def test_nominal_nya_clitic_can_head_subject_without_resolving_its_function(self):
        analyzed = self.analyze("Bukunya jatuh.")
        bound = self.token(analyzed, "bukunya")
        self.assertEqual(bound["clitic_pos_candidates"][0]["host_pos"], ["NOUN"])
        parsed = parse_sentence(analyzed)
        self.assertEqual(parsed["status"], "parsed")
        self.assertEqual(parsed["pattern"], "S-P")
        self.assertEqual(parsed["roles"]["subject"], ["bukunya"])
        self.assertEqual(parsed["roles"]["predicate"], ["jatuh"])
        self.assertEqual(parsed["clitic_analysis"], [{
            "surface": "bukunya",
            "base_form": "buku",
            "clitic": "nya",
            "function": None,
            "function_candidates": ["possessive", "definite_anaphoric"],
            "function_status": "unresolved",
            "nominal_phrase_role": "subject",
        }])

    def test_nominal_nya_possession_vs_definiteness_stays_unresolved_in_real_pipeline(self):
        analyzed = self.analyze("Dia lihat bukunya.")
        bound = self.token(analyzed, "bukunya")
        self.assertEqual(bound["clitic_pos_candidates"][0]["host_pos"], ["NOUN"])
        parsed = parse_sentence(analyzed)
        self.assertEqual(parsed["status"], "parsed")
        self.assertEqual(parsed["roles"]["object"], ["bukunya"])
        self.assertEqual(parsed["clitic_analysis"], [{
            "surface": "bukunya",
            "base_form": "buku",
            "clitic": "nya",
            "function": None,
            "function_candidates": ["possessive", "definite_anaphoric"],
            "function_status": "unresolved",
            "nominal_phrase_role": "object",
        }])

    def test_verbal_bound_clitic_is_parsed_as_object_in_real_pipeline(self):
        analyzed = self.analyze("Dia lihatku.")
        bound = self.token(analyzed, "lihatku")
        self.assertEqual(bound["status"], "unknown")
        self.assertEqual(bound["pos"], [])
        self.assertEqual(bound["clitic_pos_candidates"][0]["host_pos"], ["VERB"])
        parsed = parse_sentence(analyzed)
        self.assertEqual(parsed["status"], "parsed")
        self.assertEqual(parsed["pattern"], "S-P-O")
        self.assertEqual(parsed["roles"]["subject"], ["dia"])
        self.assertEqual(parsed["roles"]["predicate"], ["lihatku"])
        self.assertEqual(parsed["roles"]["object"], [])
        self.assertEqual(parsed["clitic_analysis"], [{
            "surface": "lihatku",
            "base_form": "lihat",
            "clitic": "ku",
            "function": "object",
            "function_status": "selected_by_verbal_host",
            "host_role": "predicate",
        }])

    def test_reflexive_diri_clitic_forms_are_recognized_without_overclaiming_function(self):
        cases = (
            ("Aku melihat diriku.", "diriku", "ku", "possessive"),
            ("Kamu melihat dirimu.", "dirimu", "mu", "possessive"),
            ("Dia melihat dirinya.", "dirinya", "nya", None),
        )
        for sentence, surface, clitic, expected_function in cases:
            with self.subTest(sentence=sentence):
                analyzed = self.analyze(sentence)
                bound = self.token(analyzed, surface)
                self.assertEqual(bound["status"], "unknown")
                self.assertEqual(bound["pos"], [])
                self.assertEqual(len(bound["clitic_pos_candidates"]), 1)
                component = bound["clitic_pos_candidates"][0]
                self.assertEqual(component["base_form"], "diri")
                self.assertEqual(component["clitic"], clitic)
                self.assertEqual(component["host_pos"], ["NOUN"])
                self.assertEqual(component["clitic_pos"], ["PRON"])

                parsed = parse_sentence(analyzed)
                self.assertEqual(parsed["roles"]["object"], [surface])
                self.assertEqual(len(parsed["clitic_analysis"]), 1)
                analysis = parsed["clitic_analysis"][0]
                self.assertEqual(analysis["surface"], surface)
                self.assertEqual(analysis["base_form"], "diri")
                self.assertEqual(analysis["clitic"], clitic)
                self.assertEqual(analysis["function"], expected_function)
                self.assertEqual(
                    analysis["reference_relation_candidates"],
                    ["reflexive", "non_reflexive"],
                )
                self.assertEqual(
                    analysis["reference_relation_status"],
                    "candidate_by_person_agreement",
                )
                self.assertIsNone(analysis["reference_relation"])
                self.assertEqual(analysis["reference_relation_candidate"], "reflexive")
                self.assertEqual(analysis["antecedent_candidate"], {
                    "ku": "aku", "mu": "kamu", "nya": "dia"
                }[clitic])

                if clitic == "nya":
                    self.assertEqual(
                        analysis["function_candidates"],
                        ["possessive", "definite_anaphoric"],
                    )
                    self.assertEqual(analysis["function_status"], "unresolved")
                else:
                    self.assertEqual(
                        analysis["function_status"], "selected_by_host_pos"
                    )

    def test_diri_clitic_person_mismatch_does_not_claim_reflexive_reference(self):
        analyzed = self.analyze("Aku melihat dirimu.")
        parsed = parse_sentence(analyzed)
        self.assertEqual(parsed["roles"]["subject"], ["aku"])
        self.assertEqual(parsed["roles"]["object"], ["dirimu"])
        analysis = parsed["clitic_analysis"][0]
        self.assertEqual(analysis["base_form"], "diri")
        self.assertIsNone(analysis["reference_relation"])
        self.assertIsNone(analysis["reference_relation_candidate"])
        self.assertEqual(
            analysis["reference_relation_candidates"],
            ["reflexive", "non_reflexive"],
        )
        self.assertEqual(analysis["reference_relation_status"], "unresolved")
        self.assertNotIn("antecedent_candidate", analysis)

    def test_all_verbal_clitic_variants_are_objects_in_real_pipeline(self):
        cases = (
            ("Dia lihatku.", "lihatku", "ku"),
            ("Dia lihatmu.", "lihatmu", "mu"),
            ("Dia lihatnya.", "lihatnya", "nya"),
        )
        for sentence, surface, clitic in cases:
            with self.subTest(sentence=sentence):
                analyzed = self.analyze(sentence)
                bound = self.token(analyzed, surface)
                self.assertEqual(bound["status"], "unknown")
                self.assertEqual(bound["pos"], [])
                self.assertEqual(bound["clitic_pos_candidates"][0]["host_pos"], ["VERB"])
                self.assertEqual(bound["clitic_pos_candidates"][0]["clitic"], clitic)
                parsed = parse_sentence(analyzed)
                self.assertEqual(parsed["status"], "parsed")
                self.assertEqual(parsed["pattern"], "S-P-O")
                self.assertEqual(parsed["roles"]["subject"], ["dia"])
                self.assertEqual(parsed["roles"]["predicate"], [surface])
                self.assertEqual(parsed["roles"]["object"], [])
                self.assertEqual(parsed["clitic_analysis"], [{
                    "surface": surface,
                    "base_form": "lihat",
                    "clitic": clitic,
                    "function": "object",
                    "function_status": "selected_by_verbal_host",
                    "host_role": "predicate",
                }])

    def test_normalization_unknown_words_and_punctuation_flow_end_to_end(self):
        result = self.analyze("  AKU   bekerja! ")
        self.assertEqual(result["normalized_text"], "aku bekerja!")
        self.assertEqual(
            [item["token"] for item in result["tokens"]],
            ["aku", "bekerja", "!"],
        )
        self.assertEqual(self.token(result, "aku")["pos"], ["PRON"])
        self.assertEqual(self.token(result, "bekerja")["pos"], ["VERB"])
        punctuation = self.token(result, "!")
        self.assertEqual(punctuation["kind"], "punctuation")
        self.assertEqual(punctuation["pos_status"], "not_applicable")


    def test_ditunda_is_verb_through_real_dictionary_pipeline(self):
        result = self.analyze("Karena hujan deras, pertandingan ditunda.")
        token = self.token(result, "ditunda")
        self.assertEqual(token["status"], "matched")
        self.assertEqual(token["pos"], ["VERB"])
        self.assertEqual(token["pos_source"], "dictionary")
        self.assertEqual(token["pos_status"], "identified")


    def test_hinggap_is_verb_through_real_dictionary_pipeline(self):
        result = self.analyze("Burung hinggap pada pagar.")
        token = self.token(result, "hinggap")
        self.assertEqual(token["status"], "matched")
        self.assertEqual(token["pos"], ["VERB"])
        self.assertEqual(token["pos_source"], "dictionary")
        self.assertEqual(token["pos_status"], "identified")


    def test_berteduh_is_verb_through_real_dictionary_pipeline(self):
        result = self.analyze("Ketika hujan turun, mereka berteduh.")
        token = self.token(result, "berteduh")
        self.assertEqual(token["status"], "matched")
        self.assertEqual(token["pos"], ["VERB"])
        self.assertEqual(token["pos_source"], "dictionary")
        self.assertEqual(token["pos_status"], "identified")


    def test_baru_is_adjective_in_nominal_phrases(self):
        for sentence in ("Mereka membaca buku baru.", "Buku baru itu milik ibu."):
            with self.subTest(sentence=sentence):
                result = self.analyze(sentence)
                token = self.token(result, "baru")
                self.assertEqual(token["status"], "matched")
                self.assertEqual(token["pos"], ["ADJ"])
                self.assertEqual(token["pos_source"], "dictionary")
                self.assertEqual(token["pos_status"], "identified")


    def test_dulu_is_adverb_in_temporal_and_sequence_contexts(self):
        for sentence in ("Gue mau makan dulu.", "Dulu dia tinggal di sini."):
            with self.subTest(sentence=sentence):
                result = self.analyze(sentence)
                token = self.token(result, "dulu")
                self.assertEqual(token["status"], "matched")
                self.assertEqual(token["pos"], ["ADV"])
                self.assertEqual(token["pos_source"], "dictionary")
                self.assertEqual(token["pos_status"], "identified")


    def test_tetap_has_adjective_and_adverb_senses_conservatively(self):
        entry = next(item for item in self.entries if item["lemma"] == "tetap")
        self.assertEqual(entry["pos"], ["ADJ", "ADV"])
        self.assertEqual([sense["pos"] for sense in entry["senses"]], [["ADJ"], ["ADV"]])

        adjective = self.analyze("pegawai tetap")
        adjective_token = self.token(adjective, "tetap")
        self.assertEqual(adjective_token["pos"], ["ADJ", "ADV"])
        self.assertIsNone(adjective_token["context_pos"])
        self.assertEqual(adjective_token["pos_context_status"], "ambiguous")

        adverb = self.analyze("mereka tetap bekerja")
        adverb_token = self.token(adverb, "tetap")
        self.assertEqual(adverb_token["pos"], ["ADJ", "ADV"])
        self.assertEqual(adverb_token["context_pos"], "ADV")
        self.assertEqual(adverb_token["pos_context_status"], "selected_by_context")



    def test_verbal_modal_with_postposed_temporal_adverb_uses_real_dictionary_pipeline(self):
        analyzed = self.analyze("Aku mau makan nasi besok.")

        for surface, expected_pos in {
            "aku": "PRON",
            "mau": "VERB",
            "makan": "VERB",
            "nasi": "NOUN",
            "besok": "ADV",
        }.items():
            token = self.token(analyzed, surface)
            self.assertEqual(token["status"], "matched")
            self.assertEqual(token["pos"], [expected_pos])
            self.assertEqual(token["pos_source"], "dictionary")
            self.assertEqual(token["pos_status"], "identified")

        parsed = parse_sentence(analyzed)
        self.assertEqual(parsed["status"], "parsed")
        self.assertEqual(parsed["pattern"], "S-P-O-K")
        self.assertEqual(parsed["roles"]["subject"], ["aku"])
        self.assertEqual(parsed["roles"]["predicate"], ["mau", "makan"])
        self.assertEqual(parsed["predicate_structure"]["head"], "makan")
        self.assertEqual(
            parsed["predicate_structure"]["modifiers"],
            [{"token": "mau", "kind": "modal"}],
        )
        self.assertEqual(parsed["roles"]["object"], ["nasi"])
        self.assertEqual(
            parsed["roles"]["adjuncts"],
            [{"adverb": "besok", "kind": "temporal"}],
        )

    def test_negation_modal_adverb_with_postposed_temporal_uses_real_pipeline(self):
        analyzed = self.analyze("Aku tidak akan makan nasi besok.")

        expected = {
            "aku": "PRON",
            "tidak": "ADV",
            "akan": "ADV",
            "makan": "VERB",
            "nasi": "NOUN",
            "besok": "ADV",
        }
        for surface, pos in expected.items():
            with self.subTest(surface=surface):
                token = self.token(analyzed, surface)
                self.assertEqual(token["status"], "matched")
                self.assertEqual(token["pos"], [pos])
                self.assertEqual(token["pos_source"], "dictionary")
                self.assertEqual(token["pos_status"], "identified")

        parsed = parse_sentence(analyzed)
        self.assertEqual(parsed["status"], "parsed")
        self.assertEqual(parsed["pattern"], "S-P-O-K")
        self.assertEqual(parsed["roles"]["subject"], ["aku"])
        self.assertEqual(parsed["roles"]["predicate"], ["tidak", "akan", "makan"])
        self.assertEqual(parsed["predicate_structure"]["head"], "makan")
        self.assertEqual(
            parsed["predicate_structure"]["modifiers"],
            [
                {"token": "tidak", "kind": "negation"},
                {"token": "akan", "kind": "modal"},
            ],
        )
        self.assertEqual(parsed["roles"]["object"], ["nasi"])
        self.assertEqual(
            parsed["roles"]["adjuncts"],
            [{"adverb": "besok", "kind": "temporal"}],
        )
    def test_ambiguous_bisa_modal_with_postposed_temporal_uses_real_pipeline(self):
        analyzed = self.analyze("Aku bisa makan nasi nanti.")

        expected = {
            "aku": "PRON",
            "makan": "VERB",
            "nasi": "NOUN",
            "nanti": "ADV",
        }
        for surface, pos in expected.items():
            with self.subTest(surface=surface):
                token = self.token(analyzed, surface)
                self.assertEqual(token["status"], "matched")
                self.assertEqual(token["pos"], [pos])
                self.assertEqual(token["pos_source"], "dictionary")
                self.assertEqual(token["pos_status"], "identified")

        bisa = self.token(analyzed, "bisa")
        self.assertEqual(bisa["status"], "matched")
        self.assertEqual(bisa["pos"], ["VERB", "NOUN"])
        self.assertEqual(bisa["context_pos"], "VERB")
        self.assertEqual(bisa["pos_context_status"], "selected_by_context")
        self.assertIn(
            {"rule": "bisa_before_verb", "pos": "VERB", "cue_token": "makan"},
            bisa["pos_context_evidence"],
        )

        parsed = parse_sentence(analyzed)
        self.assertEqual(parsed["status"], "parsed")
        self.assertEqual(parsed["pattern"], "S-P-O-K")
        self.assertEqual(parsed["roles"]["subject"], ["aku"])
        self.assertEqual(parsed["roles"]["predicate"], ["bisa", "makan"])
        self.assertEqual(parsed["predicate_structure"]["head"], "makan")
        self.assertEqual(
            parsed["predicate_structure"]["modifiers"],
            [{"token": "bisa", "kind": "modal"}],
        )
        self.assertEqual(parsed["roles"]["object"], ["nasi"])
        self.assertEqual(
            parsed["roles"]["adjuncts"],
            [{"adverb": "nanti", "kind": "temporal"}],
        )
    def test_postposed_concessive_subordinate_uses_real_dictionary_pipeline(self):
        analyzed = self.analyze("Aku pergi walaupun hujan turun.")

        expected = {
            "aku": "PRON",
            "pergi": "VERB",
            "walaupun": "CONJ",
            "hujan": "NOUN",
            "turun": "VERB",
        }
        for surface, pos in expected.items():
            with self.subTest(surface=surface):
                token = self.token(analyzed, surface)
                self.assertEqual(token["status"], "matched")
                self.assertEqual(token["pos"], [pos])
                self.assertEqual(token["pos_source"], "dictionary")
                self.assertEqual(token["pos_status"], "identified")

        parsed = parse_sentence(analyzed)
        self.assertEqual(parsed["status"], "parsed")
        self.assertEqual(parsed["pattern"], "KLAUSA-SUBORDINATIF")
        self.assertEqual(len(parsed["clauses"]), 2)
        main_clause, subordinate_clause = parsed["clauses"]
        self.assertEqual(main_clause["analysis"]["roles"]["subject"], ["aku"])
        self.assertEqual(main_clause["analysis"]["roles"]["predicate"], ["pergi"])
        self.assertEqual(subordinate_clause["subordinator"], "walaupun")
        self.assertEqual(subordinate_clause["relation_to_previous"], "konsesi")
        self.assertEqual(subordinate_clause["analysis"]["roles"]["subject"], ["hujan"])
        self.assertEqual(subordinate_clause["analysis"]["roles"]["predicate"], ["turun"])
    def test_fronted_concessive_subordinate_uses_real_dictionary_pipeline(self):
        analyzed = self.analyze("Walaupun hujan turun, aku pergi.")

        expected = {
            "walaupun": "CONJ",
            "hujan": "NOUN",
            "turun": "VERB",
            "aku": "PRON",
            "pergi": "VERB",
        }
        for surface, pos in expected.items():
            with self.subTest(surface=surface):
                token = self.token(analyzed, surface)
                self.assertEqual(token["status"], "matched")
                self.assertEqual(token["pos"], [pos])
                self.assertEqual(token["pos_source"], "dictionary")
                self.assertEqual(token["pos_status"], "identified")

        parsed = parse_sentence(analyzed)
        self.assertEqual(parsed["status"], "parsed")
        self.assertEqual(parsed["pattern"], "KLAUSA-SUBORDINATIF")
        self.assertEqual(len(parsed["clauses"]), 2)
        subordinate, main_clause = parsed["clauses"]
        self.assertEqual(subordinate["subordinator"], "walaupun")
        self.assertEqual(subordinate["relation_to_next"], "konsesi")
        self.assertEqual(subordinate["analysis"]["pattern"], "S-P")
        self.assertEqual(subordinate["analysis"]["roles"]["subject"], ["hujan"])
        self.assertEqual(subordinate["analysis"]["roles"]["predicate"], ["turun"])
        self.assertIsNone(main_clause["subordinator"])
        self.assertEqual(main_clause["relation_to_previous"], "konsesi")
        self.assertEqual(main_clause["analysis"]["pattern"], "S-P")
        self.assertEqual(main_clause["analysis"]["roles"]["subject"], ["aku"])
        self.assertEqual(main_clause["analysis"]["roles"]["predicate"], ["pergi"])
    def test_six_reflexive_and_demonstrative_lemmas_use_real_dictionary_pipeline(self):
        cases = {
            "begini": ("begini", ["ADV"]),
            "begitu": ("begitu", ["ADV"]),
            "diri": ("diri", ["NOUN"]),
            "ini": ("ini", ["PRON"]),
            "itu": ("itu", ["PRON"]),
            "sendiri": ("sendiri", ["ADJ", "ADV"]),
        }
        for surface, (lemma, expected_pos) in cases.items():
            with self.subTest(surface=surface):
                analyzed = self.analyze(surface)
                token = self.token(analyzed, surface)
                self.assertEqual(token["status"], "matched")
                self.assertEqual(token["pos"], expected_pos)
                self.assertEqual(token["pos_source"], "dictionary")
                self.assertTrue(
                    any(candidate["lemma"] == lemma for candidate in token["candidates"])
                )

    def test_demonstrative_manner_adverbs_are_distinct_from_pronouns(self):
        sentences = {
            "Begini caranya.": ("begini", ["ADV"]),
            "Jangan begitu.": ("begitu", ["ADV"]),
            "Buku ini bagus.": ("ini", ["PRON"]),
            "Rumah itu besar.": ("itu", ["PRON"]),
        }
        for sentence, (surface, expected_pos) in sentences.items():
            with self.subTest(sentence=sentence):
                analyzed = self.analyze(sentence)
                token = self.token(analyzed, surface)
                self.assertEqual(token["status"], "matched")
                self.assertEqual(token["pos"], expected_pos)
                self.assertEqual(token["pos_source"], "dictionary")
                self.assertEqual(token["pos_status"], "identified")

    def test_diri_is_nominal_and_sendiri_keeps_its_pos_ambiguity(self):
        analyzed = self.analyze("Dia melihat diri sendiri.")
        diri = self.token(analyzed, "diri")
        sendiri = self.token(analyzed, "sendiri")

        self.assertEqual(diri["status"], "matched")
        self.assertEqual(diri["pos"], ["NOUN"])
        self.assertEqual(diri["pos_status"], "identified")
        self.assertEqual(diri["pos_source"], "dictionary")

        self.assertEqual(sendiri["status"], "matched")
        self.assertEqual(sendiri["pos"], ["ADJ", "ADV"])
        self.assertIsNone(sendiri["context_pos"])
        self.assertEqual(sendiri["pos_context_status"], "ambiguous")
        self.assertEqual(sendiri["pos_source"], "dictionary")

if __name__ == "__main__":
    unittest.main()

    def test_tetap_has_adjective_and_adverb_senses_conservatively(self):
        entry = next(item for item in self.entries if item["lemma"] == "tetap")
        self.assertEqual(entry["pos"], ["ADJ", "ADV"])
        self.assertEqual([sense["pos"] for sense in entry["senses"]], [["ADJ"], ["ADV"]])

        adjective = self.analyze("pegawai tetap")
        adjective_token = self.token(adjective, "tetap")
        self.assertEqual(adjective_token["pos"], ["ADJ", "ADV"])
        self.assertIsNone(adjective_token["context_pos"])
        self.assertEqual(adjective_token["pos_context_status"], "ambiguous")

        adverb = self.analyze("mereka tetap bekerja")
        adverb_token = self.token(adverb, "tetap")
        self.assertEqual(adverb_token["pos"], ["ADJ", "ADV"])
        self.assertEqual(adverb_token["context_pos"], "ADV")
        self.assertEqual(adverb_token["pos_context_status"], "selected_by_context")

"""Regression tests for the conservative simple-clause parser."""
import unittest

from tools.parser_kalimat import parse_sentence


def token(value, pos=None, *, status=None, context=None, context_status=None, punctuation=False):
    return {
        "token": value,
        "kind": "punctuation" if punctuation else "word",
        "pos": list(pos or []),
        "pos_status": status or ("not_applicable" if punctuation else "identified" if len(pos or []) == 1 else "ambiguous"),
        "context_pos": context,
        "pos_context_status": context_status,
    }


def analysis(*items):
    return {"tokens": list(items)}


class SimpleClauseParserTests(unittest.TestCase):
    def test_parses_subject_predicate_object(self):
        result = parse_sentence(analysis(
            token("dia", ["PRON"]),
            token("makan", ["VERB"]),
            token("nasi", ["NOUN"]),
            token(".", punctuation=True),
        ))
        self.assertEqual(result["status"], "parsed")
        self.assertEqual(result["pattern"], "S-P-O")
        self.assertEqual(result["roles"]["subject"], ["dia"])
        self.assertEqual(result["roles"]["predicate"], ["makan"])
        self.assertEqual(result["roles"]["object"], ["nasi"])

    def test_parses_nominal_clitic_as_noun_phrase_without_losing_possessive_analysis(self):
        bound_noun = token("bukuku", status="unknown")
        bound_noun["clitic_pos_candidates"] = [{
            "base_form": "buku",
            "clitic": "ku",
            "host_pos": ["NOUN"],
            "clitic_pos": ["PRON"],
            "function_candidates": ["possessive", "object"],
            "function_status": "unresolved",
        }]
        result = parse_sentence(analysis(
            token("dia", ["PRON"]),
            token("lihat", ["VERB"]),
            bound_noun,
        ))
        self.assertEqual(result["status"], "parsed")
        self.assertEqual(result["pattern"], "S-P-O")
        self.assertEqual(result["roles"]["subject"], ["dia"])
        self.assertEqual(result["roles"]["predicate"], ["lihat"])
        self.assertEqual(result["roles"]["object"], ["bukuku"])
        self.assertEqual(result["clitic_analysis"], [{
            "surface": "bukuku",
            "base_form": "buku",
            "clitic": "ku",
            "function": "possessive",
            "function_status": "selected_by_host_pos",
            "nominal_phrase_role": "object",
        }])

    def test_does_not_assign_nominal_clitic_function_without_single_known_host_pos(self):
        bound_unknown = token("melihatku", status="unknown")
        bound_unknown["clitic_pos_candidates"] = [{
            "base_form": "melihat",
            "clitic": "ku",
            "host_pos": [],
            "clitic_pos": ["PRON"],
            "function_candidates": ["possessive", "object"],
            "function_status": "unresolved",
        }]
        result = parse_sentence(analysis(
            token("dia", ["PRON"]),
            bound_unknown,
        ))
        self.assertEqual(result["status"], "unresolved")
        self.assertEqual(result["clitic_analysis"], [])

    def test_parses_adverbial_predicate_and_prepositional_adjunct(self):
        result = parse_sentence(analysis(
            token("aku", ["PRON"]),
            token("sedang", ["ADV"]),
            token("bekerja", ["VERB"]),
            token("di", ["PREP"]),
            token("rumah", ["NOUN"]),
            token(".", punctuation=True),
        ))
        self.assertEqual(result["status"], "parsed")
        self.assertEqual(result["pattern"], "S-P-K")
        self.assertEqual(result["roles"]["subject"], ["aku"])
        self.assertEqual(result["roles"]["predicate"], ["sedang", "bekerja"])
        self.assertEqual(
            result["roles"]["adjuncts"],
            [{"preposition": "di", "phrase": ["rumah"]}],
        )

    def test_parses_fronted_prepositional_adjunct_before_subject(self):
        result = parse_sentence(analysis(
            token("di", ["PREP"]),
            token("rumah", ["NOUN"]),
            token("aku", ["PRON"]),
            token("bekerja", ["VERB"]),
        ))
        self.assertEqual(result["status"], "parsed")
        self.assertEqual(result["pattern"], "S-P-K")
        self.assertEqual(result["roles"]["subject"], ["aku"])
        self.assertEqual(result["roles"]["predicate"], ["bekerja"])
        self.assertEqual(
            result["roles"]["adjuncts"],
            [{"preposition": "di", "phrase": ["rumah"]}],
        )

    def test_parses_multiple_fronted_prepositional_adjuncts(self):
        result = parse_sentence(analysis(
            token("di", ["PREP"]),
            token("rumah", ["NOUN"]),
            token("pada", ["PREP"]),
            token("malam", ["NOUN"]),
            token("hari", ["NOUN"]),
            token("aku", ["PRON"]),
            token("bekerja", ["VERB"]),
        ))
        self.assertEqual(result["status"], "parsed")
        self.assertEqual(result["pattern"], "S-P-K")
        self.assertEqual(result["roles"]["subject"], ["aku"])
        self.assertEqual(result["roles"]["adjuncts"], [
            {"preposition": "di", "phrase": ["rumah"]},
            {"preposition": "pada", "phrase": ["malam", "hari"]},
        ])

    def test_does_not_absorb_unclassified_prefix_as_fronted_adjunct(self):
        result = parse_sentence(analysis(
            token("mungkin", ["ADV"]),
            token("aku", ["PRON"]),
            token("bekerja", ["VERB"]),
        ))
        self.assertEqual(result["status"], "partial")
        self.assertIn("mungkin", result["unresolved_tokens"])

    def test_parses_fronted_causal_subordinate_clause(self):
        result = parse_sentence(analysis(
            token("karena", ["CONJ"]),
            token("hujan", ["NOUN"]),
            token("turun", ["VERB"]),
            token(",", punctuation=True),
            token("aku", ["PRON"]),
            token("berteduh", ["VERB"]),
            token(".", punctuation=True),
        ))
        self.assertEqual(result["status"], "parsed")
        self.assertEqual(result["pattern"], "KLAUSA-SUBORDINATIF")
        self.assertEqual(result["clauses"][0]["subordinator"], "karena")
        self.assertEqual(result["clauses"][0]["relation_to_next"], "sebab")
        self.assertEqual(result["clauses"][0]["analysis"]["roles"]["subject"], ["hujan"])
        self.assertEqual(result["clauses"][1]["analysis"]["roles"]["subject"], ["aku"])

    def test_parses_fronted_temporal_subordinate_clause(self):
        result = parse_sentence(analysis(
            token("ketika", ["CONJ"]),
            token("malam", ["NOUN"]),
            token("tiba", ["VERB"]),
            token(",", punctuation=True),
            token("mereka", ["PRON"]),
            token("pulang", ["VERB"]),
            token(".", punctuation=True),
        ))
        self.assertEqual(result["status"], "parsed")
        self.assertEqual(result["clauses"][0]["relation_to_next"], "temporal")
        self.assertEqual(result["clauses"][1]["analysis"]["roles"]["predicate"], ["pulang"])

    def test_parses_fronted_elliptical_concessive_adjective_as_partial(self):
        result = parse_sentence(analysis(
            token("walaupun", ["CONJ"]),
            token("lelah", ["ADJ"]),
            token(",", punctuation=True),
            token("dia", ["PRON"]),
            token("bekerja", ["VERB"]),
        ))
        self.assertEqual(result["status"], "partial")
        self.assertEqual(result["pattern"], "KLAUSA-SUBORDINATIF")
        subordinate = result["clauses"][0]["analysis"]
        self.assertEqual(subordinate["pattern"], "P-ELIPTIS")
        self.assertEqual(subordinate["roles"]["subject"], [])
        self.assertEqual(subordinate["roles"]["predicate"], ["lelah"])
        self.assertIn("Subjek yang dilesapkan", subordinate["notes"][1])
        self.assertEqual(result["clauses"][0]["relation_to_next"], "konsesi")

    def test_does_not_force_unclassified_fronted_elliptical_clause(self):
        result = parse_sentence(analysis(
            token("walaupun", ["CONJ"]),
            token("mungkin", ["ADV"]),
            token(",", punctuation=True),
            token("dia", ["PRON"]),
            token("bekerja", ["VERB"]),
        ))
        self.assertNotEqual(result.get("pattern"), "KLAUSA-SUBORDINATIF")

    def test_parses_postposed_causal_subordinate_clause(self):
        result = parse_sentence(analysis(
            token("aku", ["PRON"]),
            token("pulang", ["VERB"]),
            token("karena", ["CONJ"]),
            token("hujan", ["NOUN"]),
            token("turun", ["VERB"]),
        ))
        self.assertEqual(result["status"], "parsed")
        self.assertEqual(result["pattern"], "KLAUSA-SUBORDINATIF")
        self.assertEqual(result["clauses"][0]["analysis"]["roles"]["predicate"], ["pulang"])
        self.assertEqual(result["clauses"][0]["relation_to_next"], "sebab")
        self.assertEqual(result["clauses"][1]["subordinator"], "karena")
        self.assertEqual(result["clauses"][1]["analysis"]["roles"]["subject"], ["hujan"])

    def test_parses_postposed_temporal_subordinate_clause(self):
        result = parse_sentence(analysis(
            token("aku", ["PRON"]),
            token("pulang", ["VERB"]),
            token("ketika", ["CONJ"]),
            token("malam", ["NOUN"]),
            token("tiba", ["VERB"]),
        ))
        self.assertEqual(result["pattern"], "KLAUSA-SUBORDINATIF")
        self.assertEqual(result["clauses"][1]["relation_to_previous"], "temporal")

    def test_parses_two_clauses_joined_by_conjunction(self):
        result = parse_sentence(analysis(
            token("aku", ["PRON"]),
            token("bekerja", ["VERB"]),
            token("dan", ["CONJ"]),
            token("dia", ["PRON"]),
            token("belajar", ["VERB"]),
            token(".", punctuation=True),
        ))
        self.assertEqual(result["status"], "parsed")
        self.assertEqual(result["pattern"], "KLAUSA-KOORDINATIF")
        self.assertEqual(len(result["clauses"]), 2)
        self.assertEqual(result["clauses"][0]["analysis"]["roles"]["subject"], ["aku"])
        self.assertEqual(result["clauses"][0]["analysis"]["roles"]["predicate"], ["bekerja"])
        self.assertEqual(result["clauses"][1]["connector"], "dan")
        self.assertEqual(result["clauses"][1]["analysis"]["roles"]["subject"], ["dia"])
        self.assertEqual(result["clauses"][1]["analysis"]["roles"]["predicate"], ["belajar"])

    def test_parses_three_coordinated_clauses_in_order(self):
        result = parse_sentence(analysis(
            token("aku", ["PRON"]),
            token("bekerja", ["VERB"]),
            token("dan", ["CONJ"]),
            token("dia", ["PRON"]),
            token("belajar", ["VERB"]),
            token("lalu", ["CONJ"]),
            token("mereka", ["PRON"]),
            token("bermain", ["VERB"]),
        ))
        self.assertEqual(result["status"], "parsed")
        self.assertEqual(result["pattern"], "KLAUSA-KOORDINATIF")
        self.assertEqual(len(result["clauses"]), 3)
        self.assertEqual(
            [clause["connector"] for clause in result["clauses"]],
            [None, "dan", "lalu"],
        )
        self.assertEqual(
            [clause["analysis"]["roles"]["predicate"] for clause in result["clauses"]],
            [["bekerja"], ["belajar"], ["bermain"]],
        )

    def test_classifies_causal_connector(self):
        result = parse_sentence(analysis(
            token("aku", ["PRON"]),
            token("pulang", ["VERB"]),
            token("karena", ["CONJ"]),
            token("hujan", ["NOUN"]),
            token("turun", ["VERB"]),
        ))
        self.assertEqual(result["status"], "parsed")
        self.assertEqual(result["pattern"], "KLAUSA-SUBORDINATIF")
        self.assertEqual(result["clauses"][0]["relation_to_next"], "sebab")
        self.assertEqual(result["clauses"][1]["subordinator"], "karena")
        self.assertEqual(result["clauses"][1]["relation_to_previous"], "sebab")

    def test_classifies_contrastive_connector(self):
        result = parse_sentence(analysis(
            token("aku", ["PRON"]),
            token("bekerja", ["VERB"]),
            token("namun", ["CONJ"]),
            token("dia", ["PRON"]),
            token("belajar", ["VERB"]),
        ))
        self.assertEqual(result["clauses"][1]["relation_to_previous"], "pertentangan")

    def test_classifies_concessive_connector(self):
        result = parse_sentence(analysis(
            token("aku", ["PRON"]),
            token("bekerja", ["VERB"]),
            token("walaupun", ["CONJ"]),
            token("dia", ["PRON"]),
            token("tidur", ["VERB"]),
        ))
        self.assertEqual(result["clauses"][1]["relation_to_previous"], "konsesi")

    def test_unknown_conjunction_is_not_given_guessed_relation(self):
        result = parse_sentence(analysis(
            token("aku", ["PRON"]),
            token("bekerja", ["VERB"]),
            token("penghubung", ["CONJ"]),
            token("dia", ["PRON"]),
            token("belajar", ["VERB"]),
        ))
        self.assertEqual(
            result["clauses"][1]["relation_to_previous"],
            "belum_diklasifikasikan",
        )

    def test_keeps_two_clause_coordination_backward_compatible(self):
        result = parse_sentence(analysis(
            token("aku", ["PRON"]),
            token("bekerja", ["VERB"]),
            token("dan", ["CONJ"]),
            token("dia", ["PRON"]),
            token("belajar", ["VERB"]),
        ))
        self.assertEqual(result["status"], "parsed")
        self.assertEqual(len(result["clauses"]), 2)
        self.assertEqual(result["clauses"][1]["connector"], "dan")

    def test_does_not_split_multi_conjunction_if_any_segment_has_no_verb(self):
        result = parse_sentence(analysis(
            token("aku", ["PRON"]),
            token("dan", ["CONJ"]),
            token("dia", ["PRON"]),
            token("bekerja", ["VERB"]),
            token("dan", ["CONJ"]),
            token("belajar", ["VERB"]),
        ))
        self.assertNotEqual(result["pattern"], "KLAUSA-KOORDINATIF")

    def test_does_not_split_nominal_coordination_as_two_clauses(self):
        result = parse_sentence(analysis(
            token("aku", ["PRON"]),
            token("dan", ["CONJ"]),
            token("dia", ["PRON"]),
            token("bekerja", ["VERB"]),
        ))
        self.assertEqual(result["pattern"], "S-P")
        self.assertEqual(result["roles"]["subject"], ["aku", "dan", "dia"])

    def test_does_not_split_when_second_segment_has_no_verb(self):
        result = parse_sentence(analysis(
            token("aku", ["PRON"]),
            token("membeli", ["VERB"]),
            token("nasi", ["NOUN"]),
            token("dan", ["CONJ"]),
            token("roti", ["NOUN"]),
        ))
        self.assertEqual(result["pattern"], "S-P-O")
        self.assertEqual(result["roles"]["object"], ["nasi", "dan", "roti"])

    def test_parses_coordinated_subject(self):
        result = parse_sentence(analysis(
            token("aku", ["PRON"]),
            token("dan", ["CONJ"]),
            token("dia", ["PRON"]),
            token("bekerja", ["VERB"]),
        ))
        self.assertEqual(result["status"], "parsed")
        self.assertEqual(result["pattern"], "S-P")
        self.assertEqual(result["roles"]["subject"], ["aku", "dan", "dia"])
        self.assertEqual(result["roles"]["predicate"], ["bekerja"])

    def test_parses_coordinated_object(self):
        result = parse_sentence(analysis(
            token("aku", ["PRON"]),
            token("membeli", ["VERB"]),
            token("nasi", ["NOUN"]),
            token("dan", ["CONJ"]),
            token("roti", ["NOUN"]),
        ))
        self.assertEqual(result["status"], "parsed")
        self.assertEqual(result["pattern"], "S-P-O")
        self.assertEqual(result["roles"]["object"], ["nasi", "dan", "roti"])

    def test_collects_simple_subject_phrase_with_number_and_adjective(self):
        result = parse_sentence(analysis(
            token("tiga", ["NUM"]),
            token("anak", ["NOUN"]),
            token("kecil", ["ADJ"]),
            token("makan", ["VERB"]),
            token("nasi", ["NOUN"]),
        ))
        self.assertEqual(result["status"], "parsed")
        self.assertEqual(result["pattern"], "S-P-O")
        self.assertEqual(result["roles"]["subject"], ["tiga", "anak", "kecil"])
        self.assertEqual(result["roles"]["object"], ["nasi"])

    def test_collects_simple_object_phrase_with_adjective(self):
        result = parse_sentence(analysis(
            token("dia", ["PRON"]),
            token("membeli", ["VERB"]),
            token("baju", ["NOUN"]),
            token("baru", ["ADJ"]),
        ))
        self.assertEqual(result["status"], "parsed")
        self.assertEqual(result["roles"]["object"], ["baju", "baru"])

    def test_includes_verbal_negation_in_predicate(self):
        result = parse_sentence(analysis(
            token("kami", ["PRON"]),
            token("tidak", ["ADV"]),
            token("membeli", ["VERB"]),
            token("ikan", ["NOUN"]),
        ))
        self.assertEqual(result["status"], "parsed")
        self.assertEqual(result["pattern"], "S-P-O")
        self.assertEqual(result["roles"]["predicate"], ["tidak", "membeli"])
        self.assertEqual(result["roles"]["object"], ["ikan"])

    def test_includes_temporal_negation_belum_in_predicate(self):
        result = parse_sentence(analysis(
            token("kami", ["PRON"]),
            token("belum", ["ADV"]),
            token("makan", ["VERB"]),
            token("nasi", ["NOUN"]),
        ))
        self.assertEqual(result["roles"]["predicate"], ["belum", "makan"])

    def test_groups_mau_before_lexical_verb_as_one_predicate(self):
        result = parse_sentence(analysis(
            token("aku", ["PRON"]),
            token("mau", ["VERB"]),
            token("pergi", ["VERB"]),
        ))
        self.assertEqual(result["status"], "parsed")
        self.assertEqual(result["pattern"], "S-P")
        self.assertEqual(result["roles"]["subject"], ["aku"])
        self.assertEqual(result["roles"]["predicate"], ["mau", "pergi"])

    def test_groups_ingin_before_lexical_verb_and_keeps_object(self):
        result = parse_sentence(analysis(
            token("dia", ["PRON"]),
            token("ingin", ["VERB"]),
            token("makan", ["VERB"]),
            token("nasi", ["NOUN"]),
        ))
        self.assertEqual(result["status"], "parsed")
        self.assertEqual(result["pattern"], "S-P-O")
        self.assertEqual(result["roles"]["predicate"], ["ingin", "makan"])
        self.assertEqual(result["roles"]["object"], ["nasi"])

    def test_separates_predicate_head_from_modal_negation_and_adverbial_modifiers(self):
        result = parse_sentence(analysis(
            token("aku", ["PRON"]),
            token("tidak", ["ADV"]),
            token("mau", ["VERB"]),
            token("sedang", ["ADV"]),
            token("makan", ["VERB"]),
            token("ikan", ["NOUN"]),
        ))
        self.assertEqual(result["status"], "parsed")
        self.assertEqual(result["roles"]["predicate"], ["tidak", "mau", "sedang", "makan"])
        self.assertEqual(result["predicate_structure"], {
            "head": "makan",
            "modifiers": [
                {"token": "tidak", "kind": "negation"},
                {"token": "mau", "kind": "modal"},
                {"token": "sedang", "kind": "adverbial"},
            ],
        })
        self.assertEqual(result["roles"]["object"], ["ikan"])

    def test_groups_akan_as_modal_adverb_before_lexical_verb(self):
        result = parse_sentence(analysis(
            token("dia", ["PRON"]),
            token("akan", ["ADV"]),
            token("makan", ["VERB"]),
        ))
        self.assertEqual(result["status"], "parsed")
        self.assertEqual(result["roles"]["predicate"], ["akan", "makan"])
        self.assertEqual(result["predicate_structure"], {
            "head": "makan",
            "modifiers": [{"token": "akan", "kind": "modal"}],
        })

    def test_groups_bisa_as_modal_verb_before_lexical_verb(self):
        result = parse_sentence(analysis(
            token("dia", ["PRON"]),
            token("bisa", ["VERB"]),
            token("pergi", ["VERB"]),
        ))
        self.assertEqual(result["status"], "parsed")
        self.assertEqual(result["roles"]["predicate"], ["bisa", "pergi"])
        self.assertEqual(result["predicate_structure"], {
            "head": "pergi",
            "modifiers": [{"token": "bisa", "kind": "modal"}],
        })

    def test_does_not_treat_standalone_bisa_as_modal_modifier(self):
        result = parse_sentence(analysis(
            token("dia", ["PRON"]),
            token("bisa", ["VERB"]),
        ))
        self.assertEqual(result["status"], "parsed")
        self.assertEqual(result["roles"]["predicate"], ["bisa"])
        self.assertEqual(result["predicate_structure"], {
            "head": "bisa",
            "modifiers": [],
        })

    def test_groups_negation_mau_and_lexical_verb(self):
        result = parse_sentence(analysis(
            token("dia", ["PRON"]),
            token("tidak", ["ADV"]),
            token("mau", ["VERB"]),
            token("datang", ["VERB"]),
        ))
        self.assertEqual(result["status"], "parsed")
        self.assertEqual(result["roles"]["predicate"], ["tidak", "mau", "datang"])
        self.assertEqual(result["predicate_structure"], {
            "head": "datang",
            "modifiers": [
                {"token": "tidak", "kind": "negation"},
                {"token": "mau", "kind": "modal"},
            ],
        })

    def test_modal_phrase_with_object_keeps_spo(self):
        result = parse_sentence(analysis(
            token("dia", ["PRON"]),
            token("akan", ["ADV"]),
            token("makan", ["VERB"]),
            token("nasi", ["NOUN"]),
        ))
        self.assertEqual(result["status"], "parsed")
        self.assertEqual(result["pattern"], "S-P-O")
        self.assertEqual(result["roles"]["subject"], ["dia"])
        self.assertEqual(result["roles"]["predicate"], ["akan", "makan"])
        self.assertEqual(result["roles"]["object"], ["nasi"])

    def test_modal_phrase_with_prepositional_adjunct_keeps_spk(self):
        result = parse_sentence(analysis(
            token("dia", ["PRON"]),
            token("bisa", ["VERB"]),
            token("pergi", ["VERB"]),
            token("ke", ["PREP"]),
            token("pasar", ["NOUN"]),
        ))
        self.assertEqual(result["status"], "parsed")
        self.assertEqual(result["pattern"], "S-P-K")
        self.assertEqual(result["roles"]["predicate"], ["bisa", "pergi"])
        self.assertEqual(
            result["roles"]["adjuncts"],
            [{"preposition": "ke", "phrase": ["pasar"]}],
        )

    def test_fronted_prepositional_phrase_is_not_guessed_as_subject_without_preverbal_subject(self):
        result = parse_sentence(analysis(
            token("di", ["PREP"]),
            token("rumah", ["NOUN"]),
            token("terdengar", ["VERB"]),
            token("suara", ["NOUN"]),
        ))
        self.assertEqual(result["status"], "unresolved")
        self.assertIsNone(result["pattern"])
        self.assertEqual(result["roles"]["subject"], [])
        self.assertEqual(result["roles"]["predicate"], ["terdengar"])
        self.assertEqual(result["roles"]["object"], [])
        self.assertEqual(
            result["roles"]["adjuncts"],
            [{"preposition": "di", "phrase": ["rumah"]}],
        )
        self.assertEqual(result["unresolved_tokens"], ["suara"])

    def test_fronted_prepositional_adjunct_with_modal_predicate_keeps_ksp(self):
        result = parse_sentence(analysis(
            token("di", ["PREP"]),
            token("rumah", ["NOUN"]),
            token("dia", ["PRON"]),
            token("tidak", ["ADV"]),
            token("mau", ["VERB"]),
            token("bekerja", ["VERB"]),
        ))
        self.assertEqual(result["status"], "parsed")
        self.assertEqual(result["pattern"], "S-P-K")
        self.assertEqual(result["roles"]["subject"], ["dia"])
        self.assertEqual(result["roles"]["predicate"], ["tidak", "mau", "bekerja"])
        self.assertEqual(
            result["roles"]["adjuncts"],
            [{"preposition": "di", "phrase": ["rumah"]}],
        )

    def test_parses_explicit_fronted_temporal_adverbs_before_subject(self):
        for adverb in ("besok", "nanti", "sekarang", "tadi"):
            with self.subTest(adverb=adverb):
                result = parse_sentence(analysis(
                    token(adverb, ["ADV"]),
                    token("aku", ["PRON"]),
                    token("akan", ["ADV"]),
                    token("pergi", ["VERB"]),
                ))
                self.assertEqual(result["status"], "parsed")
                self.assertEqual(result["pattern"], "S-P-K")
                self.assertEqual(result["roles"]["subject"], ["aku"])
                self.assertEqual(result["roles"]["predicate"], ["akan", "pergi"])
                self.assertEqual(
                    result["roles"]["adjuncts"],
                    [{"adverb": adverb, "kind": "temporal"}],
                )

    def test_parses_explicit_temporal_adverb_after_predicate_or_object(self):
        intransitive = parse_sentence(analysis(
            token("aku", ["PRON"]),
            token("bekerja", ["VERB"]),
            token("besok", ["ADV"]),
        ))
        self.assertEqual(intransitive["status"], "parsed")
        self.assertEqual(intransitive["pattern"], "S-P-K")
        self.assertEqual(intransitive["roles"]["predicate"], ["bekerja"])
        self.assertEqual(
            intransitive["roles"]["adjuncts"],
            [{"adverb": "besok", "kind": "temporal"}],
        )

        transitive = parse_sentence(analysis(
            token("aku", ["PRON"]),
            token("makan", ["VERB"]),
            token("nasi", ["NOUN"]),
            token("nanti", ["ADV"]),
        ))
        self.assertEqual(transitive["status"], "parsed")
        self.assertEqual(transitive["pattern"], "S-P-O-K")
        self.assertEqual(transitive["roles"]["object"], ["nasi"])
        self.assertEqual(
            transitive["roles"]["adjuncts"],
            [{"adverb": "nanti", "kind": "temporal"}],
        )

    def test_does_not_treat_unlisted_postposed_adverb_as_temporal_adjunct(self):
        result = parse_sentence(analysis(
            token("aku", ["PRON"]),
            token("bekerja", ["VERB"]),
            token("mungkin", ["ADV"]),
        ))
        self.assertEqual(result["status"], "partial")
        self.assertEqual(result["pattern"], "S-P")
        self.assertEqual(result["unresolved_tokens"], ["mungkin"])
        self.assertEqual(result["roles"]["adjuncts"], [])

    def test_does_not_treat_unlisted_fronted_adverb_as_temporal_adjunct(self):
        result = parse_sentence(analysis(
            token("mungkin", ["ADV"]),
            token("aku", ["PRON"]),
            token("pergi", ["VERB"]),
        ))
        self.assertEqual(result["status"], "partial")
        self.assertEqual(result["roles"]["subject"], ["aku"])
        self.assertEqual(result["roles"]["predicate"], ["pergi"])
        self.assertEqual(result["unresolved_tokens"], ["mungkin"])
        self.assertEqual(result["roles"]["adjuncts"], [])

    def test_modal_verb_standing_alone_remains_predicate(self):
        result = parse_sentence(analysis(
            token("aku", ["PRON"]),
            token("mau", ["VERB"]),
        ))
        self.assertEqual(result["status"], "parsed")
        self.assertEqual(result["roles"]["predicate"], ["mau"])

    def test_parses_adjectival_predicate_after_pronoun_subject(self):
        result = parse_sentence(analysis(
            token("dia", ["PRON"]),
            token("sakit", ["ADJ"]),
        ))
        self.assertEqual(result["status"], "parsed")
        self.assertEqual(result["pattern"], "S-P")
        self.assertEqual(result["roles"]["subject"], ["dia"])
        self.assertEqual(result["roles"]["predicate"], ["sakit"])

    def test_parses_adjectival_predicate_after_demonstrative_subject(self):
        result = parse_sentence(analysis(
            token("rumah", ["NOUN"]),
            token("itu", ["PRON"]),
            token("besar", ["ADJ"]),
        ))
        self.assertEqual(result["status"], "parsed")
        self.assertEqual(result["roles"]["subject"], ["rumah", "itu"])
        self.assertEqual(result["roles"]["predicate"], ["besar"])

    def test_parses_simple_nominal_predicate(self):
        result = parse_sentence(analysis(
            token("ayah", ["NOUN"]),
            token("seorang", ["NUM"]),
            token("guru", ["NOUN"]),
        ))
        self.assertEqual(result["status"], "parsed")
        self.assertEqual(result["pattern"], "S-P")
        self.assertEqual(result["roles"]["subject"], ["ayah"])
        self.assertEqual(result["roles"]["predicate"], ["seorang", "guru"])

    def test_menjadi_takes_nominal_predicate_complement(self):
        result = parse_sentence(analysis(
            token("dia", ["PRON"]),
            token("menjadi", ["VERB"]),
            token("dokter", ["NOUN"]),
        ))
        self.assertEqual(result["status"], "parsed")
        self.assertEqual(result["pattern"], "S-P-Pel")
        self.assertEqual(result["roles"]["predicate"], ["menjadi"])
        self.assertEqual(result["roles"]["object"], [])
        self.assertEqual(result["roles"]["complement"], ["dokter"])

    def test_tampak_takes_adjectival_predicate_complement(self):
        result = parse_sentence(analysis(
            token("mereka", ["PRON"]),
            token("tampak", ["VERB"]),
            token("bahagia", ["ADJ"]),
        ))
        self.assertEqual(result["status"], "parsed")
        self.assertEqual(result["pattern"], "S-P-Pel")
        self.assertEqual(result["roles"]["object"], [])
        self.assertEqual(result["roles"]["complement"], ["bahagia"])

    def test_ordinary_transitive_verb_keeps_nominal_object(self):
        result = parse_sentence(analysis(
            token("dia", ["PRON"]),
            token("membeli", ["VERB"]),
            token("baju", ["NOUN"]),
        ))
        self.assertEqual(result["status"], "parsed")
        self.assertEqual(result["pattern"], "S-P-O")
        self.assertEqual(result["roles"]["object"], ["baju"])
        self.assertEqual(result["roles"]["complement"], [])

    def test_does_not_guess_ambiguous_noun_adjective_sequence(self):
        result = parse_sentence(analysis(
            token("rumah", ["NOUN"]),
            token("besar", ["ADJ"]),
        ))
        self.assertEqual(result["status"], "unresolved")
        self.assertIsNone(result["pattern"])

    def test_uses_contextual_pos_only_when_selected(self):
        result = parse_sentence(analysis(
            token("aku", ["PRON"]),
            token("sedang", ["ADV"]),
            token("jalan", ["NOUN", "VERB"], status="identified",
                  context="VERB", context_status="selected_by_context"),
        ))
        self.assertEqual(result["roles"]["predicate"], ["sedang", "jalan"])

    def test_does_not_force_ambiguous_subject(self):
        result = parse_sentence(analysis(
            token("jalan", ["NOUN", "VERB"], status="ambiguous"),
            token("makan", ["VERB"]),
            token("nasi", ["NOUN"]),
        ))
        self.assertEqual(result["status"], "unresolved")
        self.assertIsNone(result["pattern"])
        self.assertEqual(result["roles"]["subject"], [])

    def test_abstains_on_postverbal_noun_when_kps_and_subject_ellipsis_are_ambiguous(self):
        # K-P-S candidate: postverbal noun may be the inverted subject.
        inverted = parse_sentence(analysis(
            token("di", ["PREP"]),
            token("rumah", ["NOUN"]),
            token("terdengar", ["VERB"]),
            token("suara", ["NOUN"]),
        ))
        self.assertEqual(inverted["status"], "unresolved")
        self.assertEqual(inverted["roles"]["subject"], [])
        self.assertEqual(inverted["roles"]["object"], [])
        self.assertEqual(inverted["unresolved_tokens"], ["suara"])

        # Same surface order can also contain an omitted subject plus an object.
        omitted_subject = parse_sentence(analysis(
            token("di", ["PREP"]),
            token("rumah", ["NOUN"]),
            token("membaca", ["VERB"]),
            token("buku", ["NOUN"]),
        ))
        self.assertEqual(omitted_subject["status"], "unresolved")
        self.assertEqual(omitted_subject["roles"]["subject"], [])
        self.assertEqual(omitted_subject["roles"]["object"], [])
        self.assertEqual(omitted_subject["unresolved_tokens"], ["buku"])

    def test_does_not_guess_postverbal_subject_in_kps_inversion(self):
        # "Terjadi kecelakaan" is K-P-S; inversion is not supported yet.
        # The postverbal noun must not be relabeled as an object.
        result = parse_sentence(analysis(
            token("terjadi", ["VERB"]),
            token("kecelakaan", ["NOUN"]),
        ))
        self.assertEqual(result["status"], "unresolved")
        self.assertIsNone(result["pattern"])
        self.assertEqual(result["roles"]["subject"], [])
        self.assertEqual(result["roles"]["object"], [])
        self.assertIn("inversi", result["notes"][0])

    def test_returns_unresolved_when_no_certain_verb(self):
        result = parse_sentence(analysis(
            token("rumah", ["NOUN"]),
            token("besar", ["ADJ"]),
        ))
        self.assertEqual(result["status"], "unresolved")
        self.assertIn("Predikat VERB atau pola predikat nonverbal sederhana", result["notes"][0])

    def test_internal_comma_is_not_misparsed_as_one_clause(self):
        result = parse_sentence(analysis(
            token("aku", ["PRON"]),
            token("makan", ["VERB"]),
            token(",", punctuation=True),
            token("dia", ["PRON"]),
            token("tidur", ["VERB"]),
        ))
        self.assertEqual(result["status"], "unsupported")
        self.assertIsNone(result["pattern"])

    def test_rejects_invalid_input(self):
        with self.assertRaises(TypeError):
            parse_sentence([])
        with self.assertRaises(ValueError):
            parse_sentence({})


if __name__ == "__main__":
    unittest.main()

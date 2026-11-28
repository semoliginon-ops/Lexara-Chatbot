"""One bounded read-only composition test using the real dictionary pipeline."""
import unittest
from pathlib import Path

from tools.analisis_teks import analyze_text
from tools.clarification_interaction import (
    prepare_clarification_prompt,
    record_clarification_response,
)
from tools.clarification_planner import plan_clarification
from tools.context_snapshot import build_context_snapshot
from tools.kamus_loader import load_dictionary_directory
from tools.parser_kalimat import parse_sentence
from tools.pencocokan_kamus import build_lexicon
from tools.pos_context import disambiguate_pos_context
from tools.pos_tagger import tag_pos
from tools.utterance_interpretation import interpret_utterance


class ClarificationInteractionPipelineTests(unittest.TestCase):
    def test_real_bangun_dictionary_pipeline_to_prompt_and_choice_record(self):
        root = Path(__file__).resolve().parents[1]
        entries = load_dictionary_directory(root / "data" / "kamus")
        lexicon = build_lexicon(entries)

        analysis = analyze_text("Aku bangun.", lexicon)
        tagged = disambiguate_pos_context(tag_pos(analysis))
        parse_result = parse_sentence(tagged)
        snapshot = build_context_snapshot(tagged, parse_result)
        report = interpret_utterance(snapshot)

        ambiguity_item = next(
            item for item in report["ambiguity"]["items"]
            if item["dimension"] == "lexical_sense"
            and snapshot["tokens"][item["token_index"]]["token"].casefold() == "bangun"
        )
        token_index = ambiguity_item["token_index"]
        parent_ref = ambiguity_item["candidate_refs"][0]
        candidate = snapshot["tokens"][token_index]["lexical_candidates"][
            parent_ref["candidate_index"]
        ]
        senses = candidate["entry"]["senses"]
        sense_refs = [
            {
                "source_field": "lexical_candidates",
                "token_index": token_index,
                "candidate_index": parent_ref["candidate_index"],
                "sense_index": sense_index,
                "sense_id": sense["sense_id"],
            }
            for sense_index, sense in enumerate(senses)
            if isinstance(sense.get("definition"), str) and sense["definition"].strip()
        ]
        self.assertGreaterEqual(len(sense_refs), 2)

        plan = plan_clarification(report, [{
            "ambiguity_item_index": report["ambiguity"]["items"].index(ambiguity_item),
            "parent_candidate_ref": parent_ref,
            "sense_refs": sense_refs,
            "material_to_next_response": True,
            "user_can_distinguish": True,
            "priority": 0,
        }], snapshot=snapshot)
        self.assertEqual(plan["decision"], "ask")

        presented = prepare_clarification_prompt(
            plan, snapshot, "pipeline-session-bangun"
        )
        self.assertEqual(presented["status"], "presented")
        self.assertIn("bangun", presented["prompt"]["text"].casefold())
        self.assertEqual(len(presented["prompt"]["choices"]), 2)

        recorded = record_clarification_response(
            presented["session"],
            {"type": "choice", "choice_key": "option_2"},
        )
        self.assertEqual(recorded["status"], "answered_choice")
        self.assertEqual(
            recorded["session"]["response"]["sense_ref"]["sense_id"],
            senses[1]["sense_id"],
        )


if __name__ == "__main__":
    unittest.main()

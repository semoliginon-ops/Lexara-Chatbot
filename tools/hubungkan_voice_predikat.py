"""Penghubung konservatif bukti voice token dengan kepala predikat parser."""
from __future__ import annotations

from typing import Any


def connect_predicate_voice(
    parse_result: dict[str, Any],
    text_analysis: dict[str, Any],
) -> dict[str, Any]:
    """Attach token-level morphological voice evidence to one parsed predicate.

    Only a fully parsed flat simple clause is supported. Clause trees, partial
    parses, missing heads, repeated head forms, and uncertain token voice all
    abstain rather than guessing token alignment or sentence voice.
    """
    if not isinstance(parse_result, dict):
        raise TypeError("parse_result harus berupa dictionary")
    if not isinstance(text_analysis, dict):
        raise TypeError("text_analysis harus berupa dictionary")

    def unresolved(reason: str, head: str | None = None) -> dict[str, Any]:
        return {
            "status": "unresolved",
            "voice": None,
            "reason": reason,
            "predicate_head": head,
            "token_index": None,
            "evidence": [],
        }

    if parse_result.get("status") != "parsed":
        return unresolved("parser_not_fully_resolved")
    if parse_result.get("parser_method") != "conservative_svo_v4":
        return unresolved("non_flat_clause_structure")

    structure = parse_result.get("predicate_structure")
    if not isinstance(structure, dict):
        return unresolved("predicate_head_unavailable")
    head = structure.get("head")
    if not isinstance(head, str) or not head:
        return unresolved("predicate_head_unavailable")

    tokens = text_analysis.get("tokens")
    if not isinstance(tokens, list):
        raise ValueError("text_analysis harus memiliki array tokens")

    matches = [
        (index, item)
        for index, item in enumerate(tokens)
        if isinstance(item, dict)
        and item.get("kind") == "word"
        and item.get("token") == head
    ]
    if not matches:
        return unresolved("predicate_head_not_found_in_token_analysis", head)
    if len(matches) != 1:
        return unresolved("predicate_head_token_alignment_ambiguous", head)

    index, token = matches[0]
    voice_result = token.get("voice_analysis")
    if not isinstance(voice_result, dict):
        return unresolved("token_voice_evidence_unavailable", head)
    if voice_result.get("status") != "identified":
        reason = voice_result.get("reason")
        return unresolved(
            reason if isinstance(reason, str) else "token_voice_not_identified",
            head,
        )
    voice = voice_result.get("voice")
    if voice not in {"active", "passive"}:
        return unresolved("invalid_identified_token_voice", head)

    evidence = voice_result.get("evidence")
    return {
        "status": "identified",
        "voice": voice,
        "reason": "predicate_head_token_voice_evidence",
        "predicate_head": head,
        "token_index": index,
        "evidence": evidence if isinstance(evidence, list) else [],
        "notes": [
            "Bukti voice diambil dari token yang cocok tepat dengan kepala predikat parser.",
            "Hasil hanya berlaku untuk klausa sederhana yang diparse penuh; ini bukan penentuan voice untuk seluruh kalimat majemuk.",
        ],
    }

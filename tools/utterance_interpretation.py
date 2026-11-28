"""Read-only reporting of explicit ambiguity and communicative form.

This module consumes Context Snapshot v1. It does not rerun or modify upstream
language components and deliberately abstains outside a small explicit scope.
"""
from __future__ import annotations

from typing import Any


class UtteranceInterpretationError(ValueError):
    """Snapshot input does not satisfy the minimum v1 shape."""


def _validate_snapshot(snapshot: Any) -> None:
    if not isinstance(snapshot, dict):
        raise UtteranceInterpretationError("snapshot harus berupa object")
    if not isinstance(snapshot.get("tokens"), list):
        raise UtteranceInterpretationError("snapshot.tokens harus berupa list")
    text = snapshot.get("normalized_text")
    if text is not None and not isinstance(text, str):
        raise UtteranceInterpretationError("normalized_text harus berupa teks atau null")
    for index, item in enumerate(snapshot["tokens"]):
        if not isinstance(item, dict) or not isinstance(item.get("token"), str):
            raise UtteranceInterpretationError(
                f"tokens[{index}] harus berupa object dengan token teks"
            )


def _candidate_refs(field: str, token_index: int, candidates: list[Any]) -> list[dict[str, Any]]:
    return [
        {
            "source_field": field,
            "token_index": token_index,
            "candidate_index": index,
        }
        for index, _ in enumerate(candidates)
    ]


def _token_ambiguities(item: dict[str, Any], index: int) -> list[dict[str, Any]]:
    notes: list[dict[str, Any]] = []

    lexical = item.get("lexical_candidates", [])
    if not isinstance(lexical, list):
        lexical = []
    multiple_senses = any(
        isinstance(candidate, dict)
        and (
            (
                isinstance(candidate.get("sense_ids"), list)
                and len(candidate["sense_ids"]) > 1
            )
            or (
                isinstance(candidate.get("entry"), dict)
                and isinstance(candidate["entry"].get("senses"), list)
                and len(candidate["entry"]["senses"]) > 1
            )
        )
        for candidate in lexical
    )
    if len(lexical) > 1 or multiple_senses or item.get("lexical_status") == "ambiguous":
        notes.append({
            "dimension": "lexical_sense",
            "token_index": index,
            "candidate_refs": _candidate_refs("lexical_candidates", index, lexical),
            "evidence_refs": [{
                "source_field": "lexical_status",
                "token_index": index,
            }],
            "status": "ambiguous",
            "reason": "multiple_candidates_preserved",
        })

    pos_candidates = item.get("pos_candidates", [])
    if not isinstance(pos_candidates, list):
        pos_candidates = []
    pos_values = item.get("pos", [])
    has_multiple_pos = isinstance(pos_values, list) and len(set(
        value for value in pos_values if isinstance(value, str)
    )) > 1
    if len(pos_candidates) > 1 or has_multiple_pos:
        notes.append({
            "dimension": "pos",
            "token_index": index,
            "candidate_refs": _candidate_refs("pos_candidates", index, pos_candidates),
            "evidence_refs": [{
                "source_field": "pos_status",
                "token_index": index,
            }, {
                "source_field": "pos_candidates",
                "token_index": index,
            }],
            "status": "ambiguous",
            "reason": "multiple_pos_candidates_preserved",
        })

    syntax_status = item.get("syntax_status")
    if syntax_status in {"unresolved", "deferred"}:
        notes.append({
            "dimension": "syntax",
            "token_index": index,
            "candidate_refs": [],
            "evidence_refs": [{
                "source_field": "syntax_status",
                "token_index": index,
            }, {
                "source_field": "syntax_reason",
                "token_index": index,
            }],
            "status": syntax_status,
            "reason": item.get("syntax_reason") or (
                "parser_reports_unresolved" if syntax_status == "unresolved"
                else "parser_mapping_deferred"
            ),
        })
    return notes


def _summary_status(items: list[dict[str, Any]], snapshot_status: Any) -> str:
    statuses = [item["status"] for item in items]
    for status in ("deferred", "unresolved", "ambiguous"):
        if status in statuses:
            return status
    if snapshot_status == "deferred":
        return "deferred"
    return "resolved"


def _classify_intent(snapshot: dict[str, Any]) -> dict[str, Any]:
    text = snapshot.get("normalized_text") or ""
    tokens = [
        item["token"].casefold()
        for item in snapshot["tokens"]
        if item.get("kind", "word") == "word"
    ]
    candidates: list[tuple[str, str, str]] = []
    if "?" in text:
        candidates.append(("question", "normalized_text", "explicit_question_mark"))
    if "tolong" in tokens:
        candidates.append(("request", "tokens", "explicit_marker_tolong"))
    if "jangan" in tokens:
        candidates.append(("directive", "tokens", "explicit_marker_jangan"))

    # Keep deterministic order and avoid duplicate labels.
    unique: list[tuple[str, str, str]] = []
    seen: set[str] = set()
    for candidate in candidates:
        if candidate[0] not in seen:
            unique.append(candidate)
            seen.add(candidate[0])

    labels = [item[0] for item in unique]
    evidence: list[dict[str, Any]] = []
    for label, field, _ in unique:
        reference: dict[str, Any] = {"source_field": field}
        if field == "tokens":
            marker = "tolong" if label == "request" else "jangan"
            token_index = next(
                index for index, item in enumerate(snapshot["tokens"])
                if item.get("kind", "word") == "word"
                and item["token"].casefold() == marker
            )
            reference["token_index"] = token_index
        evidence.append(reference)

    if len(unique) == 1:
        return {
            "status": "resolved",
            "label": labels[0],
            "labels": labels,
            "candidates": [labels[0]],
            "evidence_refs": evidence,
            "reason": unique[0][2],
        }
    if len(unique) > 1:
        return {
            "status": "resolved",
            "label": None,
            "labels": labels,
            "candidates": [],
            "evidence_refs": evidence,
            "reason": "multiple_coexisting_explicit_forms",
        }
    return {
        "status": "unresolved",
        "label": "unknown",
        "labels": [],
        "candidates": [],
        "evidence_refs": [],
        "reason": "insufficient_explicit_evidence",
    }


def interpret_utterance(snapshot: dict[str, Any]) -> dict[str, Any]:
    """Return a traceable ambiguity and communicative-form report."""
    _validate_snapshot(snapshot)
    items: list[dict[str, Any]] = []
    for index, item in enumerate(snapshot["tokens"]):
        if item.get("kind", "word") == "word":
            items.extend(_token_ambiguities(item, index))

    return {
        "schema_version": "1.0",
        "source": {
            "snapshot_status": snapshot.get("status"),
            "parser_status": snapshot.get("parser_status"),
        },
        "ambiguity": {
            "status": _summary_status(items, snapshot.get("status")),
            "items": items,
        },
        "communicative_intent": _classify_intent(snapshot),
    }

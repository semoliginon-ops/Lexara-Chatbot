"""Select a lexical sense conservatively from explicit contextual evidence.

This module consumes evidence from Context Evidence Generator v1. It does not
generate evidence, alter candidates, or integrate with the runtime pipeline.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Any


class ContextualSenseSelectorError(ValueError):
    """Input data does not satisfy the contextual sense selector contract."""


_POLARITIES = {"supports", "contradicts"}
_STRENGTHS = {"weak", "strong"}


def _nonempty_text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ContextualSenseSelectorError(
            f"{label} harus berupa teks nonkosong"
        )
    return value


def _validate_candidates(
    sense_candidates: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    if not isinstance(sense_candidates, list):
        raise ContextualSenseSelectorError(
            "sense_candidates harus berupa list"
        )

    candidates: list[dict[str, Any]] = []
    seen_senses: set[str] = set()
    for index, candidate in enumerate(sense_candidates):
        label = f"sense_candidates[{index}]"
        if not isinstance(candidate, dict):
            raise ContextualSenseSelectorError(
                f"{label} harus berupa object"
            )
        sense_id = _nonempty_text(
            candidate.get("sense_id"), f"{label}.sense_id"
        )
        if sense_id in seen_senses:
            raise ContextualSenseSelectorError(
                f"sense_id kandidat duplikat: {sense_id}"
            )
        seen_senses.add(sense_id)
        candidates.append(deepcopy(candidate))
    return candidates


def _validate_evidence(
    evidence: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    if not isinstance(evidence, list):
        raise ContextualSenseSelectorError("evidence harus berupa list")

    validated: list[dict[str, Any]] = []
    for index, item in enumerate(evidence):
        label = f"evidence[{index}]"
        if not isinstance(item, dict):
            raise ContextualSenseSelectorError(
                f"{label} harus berupa object"
            )
        sense_id = _nonempty_text(
            item.get("sense_id"), f"{label}.sense_id"
        )
        polarity = item.get("polarity")
        if polarity not in _POLARITIES:
            raise ContextualSenseSelectorError(
                f"{label}.polarity harus supports atau contradicts"
            )
        strength = item.get("strength")
        if strength not in _STRENGTHS:
            raise ContextualSenseSelectorError(
                f"{label}.strength harus weak atau strong"
            )
        copied = deepcopy(item)
        copied["sense_id"] = sense_id
        validated.append(copied)
    return validated


def select_contextual_sense(
    sense_candidates: list[dict[str, Any]],
    evidence: list[dict[str, Any]],
) -> dict[str, Any]:
    """Choose a sense only when strong evidence excludes every alternative.

    The candidate list must describe one occurrence of a lexical token.
    Weak evidence is retained for audit but never contributes to a decision.
    Evidence referring to a sense outside this candidate group is ignored and
    reported. Neither input is mutated.
    """
    candidates = _validate_candidates(sense_candidates)
    validated_evidence = _validate_evidence(evidence)
    candidate_ids = {item["sense_id"] for item in candidates}

    evidence_by_sense: dict[str, list[dict[str, Any]]] = {
        item["sense_id"]: [] for item in candidates
    }
    ignored_evidence: list[dict[str, Any]] = []
    for item in validated_evidence:
        if item["sense_id"] not in candidate_ids:
            ignored = deepcopy(item)
            ignored["ignored_reason"] = "unknown_sense"
            ignored_evidence.append(ignored)
        else:
            evidence_by_sense[item["sense_id"]].append(item)

    candidate_audit: list[dict[str, Any]] = []
    viable_ids: list[str] = []
    conflicted_ids: list[str] = []
    all_used_evidence: list[dict[str, Any]] = []

    for candidate in candidates:
        sense_id = candidate["sense_id"]
        items = evidence_by_sense[sense_id]
        strong_supports = [
            item for item in items
            if item["strength"] == "strong"
            and item["polarity"] == "supports"
        ]
        strong_contradictions = [
            item for item in items
            if item["strength"] == "strong"
            and item["polarity"] == "contradicts"
        ]
        weak_items = [
            item for item in items if item["strength"] == "weak"
        ]

        if strong_supports and strong_contradictions:
            state = "conflicted"
            conflicted_ids.append(sense_id)
            viable_ids.append(sense_id)
        elif strong_contradictions:
            state = "excluded"
        else:
            state = "viable"
            viable_ids.append(sense_id)

        candidate_audit.append({
            "sense_id": sense_id,
            "candidate": deepcopy(candidate),
            "state": state,
            "strong_supports": deepcopy(strong_supports),
            "strong_contradictions": deepcopy(strong_contradictions),
            "weak_evidence": deepcopy(weak_items),
        })
        all_used_evidence.extend(deepcopy(items))

    selected_sense_id: str | None = None
    if not candidates:
        status = "unresolved"
        reason = "no_candidates"
    elif len(candidates) == 1:
        only = candidate_audit[0]
        if only["state"] == "viable":
            status = "not_needed"
            reason = "single_candidate_no_context_decision"
        else:
            status = "unresolved"
            reason = "strong_evidence_conflict"
    elif len(viable_ids) > 1:
        status = "ambiguous"
        if conflicted_ids:
            reason = "strong_evidence_conflict"
        else:
            reason = "multiple_viable_senses"
    elif len(viable_ids) == 1:
        only_id = viable_ids[0]
        only = next(
            item for item in candidate_audit
            if item["sense_id"] == only_id
        )
        if only["state"] == "conflicted":
            status = "unresolved"
            reason = "strong_evidence_conflict"
        elif only["strong_supports"]:
            status = "selected"
            reason = "one_sense_supported_all_alternatives_excluded"
            selected_sense_id = only_id
        else:
            status = "unresolved"
            reason = "insufficient_strong_evidence"
    else:
        status = "unresolved"
        reason = (
            "strong_evidence_conflict"
            if conflicted_ids or candidates
            else "insufficient_strong_evidence"
        )

    return {
        "status": status,
        "reason": reason,
        "selected_sense_id": selected_sense_id,
        "candidate_audit": candidate_audit,
        "used_evidence": all_used_evidence,
        "ignored_evidence": ignored_evidence,
    }

"""Plan one safe clarification focus from explicit interpretation evidence.

This module does not generate user-facing wording or manage dialogue state.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Any


class ClarificationPlannerError(ValueError):
    """Interpretation report does not satisfy the minimum v1 shape."""


_VALID_STATUSES = {"resolved", "ambiguous", "unresolved", "deferred"}


def _validate_report(report: Any) -> None:
    if not isinstance(report, dict):
        raise ClarificationPlannerError("report harus berupa object")
    ambiguity = report.get("ambiguity")
    if not isinstance(ambiguity, dict):
        raise ClarificationPlannerError("report.ambiguity harus berupa object")
    if ambiguity.get("status") not in _VALID_STATUSES:
        raise ClarificationPlannerError("status ambiguity tidak dikenal")
    items = ambiguity.get("items")
    if not isinstance(items, list):
        raise ClarificationPlannerError("ambiguity.items harus berupa list")
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            raise ClarificationPlannerError(
                f"ambiguity.items[{index}] harus berupa object"
            )
        if item.get("status") not in _VALID_STATUSES:
            raise ClarificationPlannerError(
                f"status ambiguity.items[{index}] tidak dikenal"
            )
        refs = item.get("candidate_refs", [])
        if not isinstance(refs, list) or any(
            not isinstance(ref, dict) for ref in refs
        ):
            raise ClarificationPlannerError(
                f"candidate_refs item {index} harus berupa list object"
            )


def _abstain(reason: str, schema_version: str = "1.0") -> dict[str, Any]:
    return {
        "schema_version": schema_version,
        "decision": "abstain",
        "reason": reason,
        "focus": None,
    }


def _valid_index(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def _validate_sense_reference(
    sense_ref: Any,
    parent_ref: dict[str, Any],
    item: dict[str, Any],
    snapshot: Any,
) -> bool:
    if not isinstance(sense_ref, dict):
        return False
    if sense_ref.get("source_field") != "lexical_candidates":
        return False
    token_index = sense_ref.get("token_index")
    candidate_index = sense_ref.get("candidate_index")
    sense_index = sense_ref.get("sense_index")
    sense_id = sense_ref.get("sense_id")
    if not all(_valid_index(value) for value in (
        token_index, candidate_index, sense_index
    )):
        return False
    if (
        token_index != item.get("token_index")
        or token_index != parent_ref.get("token_index")
        or candidate_index != parent_ref.get("candidate_index")
        or not isinstance(sense_id, str)
        or not sense_id.strip()
    ):
        return False
    if not isinstance(snapshot, dict) or not isinstance(snapshot.get("tokens"), list):
        return False
    tokens = snapshot["tokens"]
    if token_index >= len(tokens) or not isinstance(tokens[token_index], dict):
        return False
    lexical = tokens[token_index].get("lexical_candidates")
    if not isinstance(lexical, list) or candidate_index >= len(lexical):
        return False
    candidate = lexical[candidate_index]
    if not isinstance(candidate, dict):
        return False
    entry = candidate.get("entry")
    if not isinstance(entry, dict):
        return False
    senses = entry.get("senses")
    if not isinstance(senses, list) or sense_index >= len(senses):
        return False
    sense = senses[sense_index]
    if not isinstance(sense, dict):
        return False
    definition = sense.get("definition")
    return (
        sense.get("sense_id") == sense_id
        and isinstance(definition, str)
        and bool(definition.strip())
    )


def plan_clarification(
    report: dict[str, Any],
    opportunities: list[dict[str, Any]] | None = None,
    snapshot: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Return at most one traceable clarification focus."""
    _validate_report(report)
    if opportunities is not None and not isinstance(opportunities, list):
        return _abstain("invalid_opportunities")

    ambiguity = report["ambiguity"]
    items = ambiguity["items"]
    if ambiguity["status"] == "deferred" or any(
        item["status"] == "deferred" for item in items
    ):
        return {
            "schema_version": "1.0",
            "decision": "defer",
            "reason": "source_or_interpretation_deferred",
            "focus": None,
        }
    if not items:
        return {
            "schema_version": "1.0",
            "decision": "proceed",
            "reason": "no_relevant_ambiguity",
            "focus": None,
        }

    if opportunities is None:
        opportunities = []
    if not opportunities:
        return _abstain("no_valid_clarification_opportunity")

    valid_opportunities: list[tuple[int, int, dict[str, Any], str]] = []
    all_non_actionable = True
    for opportunity in opportunities:
        if not isinstance(opportunity, dict):
            return _abstain("invalid_opportunity")
        index = opportunity.get("ambiguity_item_index")
        material = opportunity.get("material_to_next_response")
        distinguishable = opportunity.get("user_can_distinguish")
        priority = opportunity.get("priority")
        if (
            not _valid_index(index)
            or index >= len(items)
            or not isinstance(material, bool)
            or not isinstance(distinguishable, bool)
            or not _valid_index(priority)
        ):
            return _abstain("invalid_opportunity")

        source_item = items[index]
        has_candidate_refs = "candidate_refs" in opportunity
        has_sense_refs = (
            "parent_candidate_ref" in opportunity or "sense_refs" in opportunity
        )
        if has_candidate_refs == has_sense_refs:
            return _abstain("invalid_opportunity_reference_shape")

        if has_candidate_refs:
            refs = opportunity.get("candidate_refs")
            if (
                not isinstance(refs, list) or len(refs) < 2
                or any(not isinstance(ref, dict) for ref in refs)
                or any(
                    ref == previous
                    for position, ref in enumerate(refs)
                    for previous in refs[:position]
                )
            ):
                return _abstain("invalid_opportunity")
            source_refs = source_item["candidate_refs"]
            if (
                source_item["status"] != "ambiguous"
                or any(ref not in source_refs for ref in refs)
            ):
                return _abstain("untraceable_candidate_reference")
            focus = {"ambiguity_item_index": index, "candidate_refs": deepcopy(refs)}
            schema_version = "1.0"
        else:
            parent_ref = opportunity.get("parent_candidate_ref")
            sense_refs = opportunity.get("sense_refs")
            if (
                source_item["status"] != "ambiguous"
                or source_item.get("dimension") != "lexical_sense"
                or not isinstance(parent_ref, dict)
                or parent_ref not in source_item["candidate_refs"]
                or not isinstance(sense_refs, list)
                or len(sense_refs) < 2
                or any(
                    sense_ref == previous
                    for position, sense_ref in enumerate(sense_refs)
                    for previous in sense_refs[:position]
                )
                or any(
                    not _validate_sense_reference(
                        sense_ref, parent_ref, source_item, snapshot
                    )
                    for sense_ref in sense_refs
                )
            ):
                return _abstain("invalid_or_untraceable_sense_reference", "1.1")
            focus = {
                "ambiguity_item_index": index,
                "parent_candidate_ref": deepcopy(parent_ref),
                "sense_refs": deepcopy(sense_refs),
            }
            schema_version = "1.1"

        if material and distinguishable:
            all_non_actionable = False
            valid_opportunities.append((priority, index, focus, schema_version))

    if not valid_opportunities:
        if all_non_actionable:
            return {
                "schema_version": "1.1" if any(
                    "sense_refs" in opportunity for opportunity in opportunities
                    if isinstance(opportunity, dict)
                ) else "1.0",
                "decision": "proceed",
                "reason": "no_material_user_distinguishable_uncertainty",
                "focus": None,
            }
        return _abstain("no_valid_clarification_opportunity")

    priority, index, focus, schema_version = min(
        valid_opportunities, key=lambda item: (item[0], item[1])
    )
    return {
        "schema_version": schema_version,
        "decision": "ask",
        "reason": (
            "one_material_user_distinguishable_sense_ambiguity"
            if "sense_refs" in focus
            else "one_material_user_distinguishable_ambiguity"
        ),
        "focus": focus,
    }

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


def _abstain(reason: str) -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "decision": "abstain",
        "reason": reason,
        "focus": None,
    }


def plan_clarification(
    report: dict[str, Any],
    opportunities: list[dict[str, Any]] | None = None,
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

    valid_opportunities: list[tuple[int, int, list[dict[str, Any]]]] = []
    all_non_actionable = True
    for opportunity in opportunities:
        if not isinstance(opportunity, dict):
            return _abstain("invalid_opportunity")
        index = opportunity.get("ambiguity_item_index")
        refs = opportunity.get("candidate_refs")
        material = opportunity.get("material_to_next_response")
        distinguishable = opportunity.get("user_can_distinguish")
        priority = opportunity.get("priority")
        if (
            isinstance(index, bool) or not isinstance(index, int)
            or index < 0 or index >= len(items)
            or not isinstance(refs, list) or len(refs) < 2
            or any(not isinstance(ref, dict) for ref in refs)
            or len({tuple(sorted(ref.items())) for ref in refs}) != len(refs)
            or not isinstance(material, bool)
            or not isinstance(distinguishable, bool)
            or isinstance(priority, bool) or not isinstance(priority, int)
            or priority < 0
        ):
            return _abstain("invalid_opportunity")
        source_item = items[index]
        source_refs = source_item["candidate_refs"]
        if (
            source_item["status"] != "ambiguous"
            or any(ref not in source_refs for ref in refs)
        ):
            return _abstain("untraceable_candidate_reference")
        if material and distinguishable:
            all_non_actionable = False
            valid_opportunities.append((priority, index, deepcopy(refs)))

    if not valid_opportunities:
        if all_non_actionable:
            return {
                "schema_version": "1.0",
                "decision": "proceed",
                "reason": "no_material_user_distinguishable_uncertainty",
                "focus": None,
            }
        return _abstain("no_valid_clarification_opportunity")

    priority, index, refs = min(
        valid_opportunities, key=lambda item: (item[0], item[1])
    )
    return {
        "schema_version": "1.0",
        "decision": "ask",
        "reason": "one_material_user_distinguishable_ambiguity",
        "focus": {
            "ambiguity_item_index": index,
            "candidate_refs": refs,
        },
    }

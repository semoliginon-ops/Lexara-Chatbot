"""Read-only snapshot that combines lexical, morphology, POS, and parser output."""
from __future__ import annotations

from copy import deepcopy
from typing import Any


_ROLE_FIELDS = (
    ("subject", "subject"),
    ("predicate", "predicate"),
    ("object", "object"),
    ("adjuncts", "adjunct"),
    ("complement", "complement"),
)


class ContextSnapshotError(ValueError):
    """Input does not satisfy the context snapshot contract."""


def _collect_role_tokens(value: Any) -> list[str]:
    """Collect only token strings exposed by the parser's documented role shapes."""
    if isinstance(value, str):
        return [value] if value.strip() else []
    if isinstance(value, list):
        result: list[str] = []
        for item in value:
            result.extend(_collect_role_tokens(item))
        return result
    if isinstance(value, dict):
        result: list[str] = []
        for key in ("adverb", "preposition", "phrase"):
            if key in value:
                result.extend(_collect_role_tokens(value[key]))
        return result
    return []


def _casefold_counts(values: list[str]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for value in values:
        key = value.casefold()
        counts[key] = counts.get(key, 0) + 1
    return counts


def _token_snapshot(
    index: int,
    item: dict[str, Any],
    source_counts: dict[str, int],
    role_counts: dict[str, dict[str, int]],
    unresolved_counts: dict[str, int],
    parser_status: str,
    has_clauses: bool,
) -> dict[str, Any]:
    token = item["token"]
    kind = item.get("kind", "word")
    base = {
        "token_index": index,
        "token": token,
        "kind": kind,
        "source": deepcopy(item),
        "lexical_status": deepcopy(item.get("status")),
        "lexical_candidates": deepcopy(item.get("candidates", [])),
        "morphology_candidates": deepcopy(item.get("morphology_candidates", [])),
        "voice_analysis": deepcopy(item.get("voice_analysis")),
        "pos_candidates": deepcopy(item.get("pos_candidates", [])),
        "pos": deepcopy(item.get("pos", [])),
        "pos_status": deepcopy(item.get("pos_status")),
        "context_pos": deepcopy(item.get("context_pos")),
        "pos_context_status": deepcopy(item.get("pos_context_status")),
        "pos_context_evidence": deepcopy(item.get("pos_context_evidence", [])),
        "clitic_pos_candidates": deepcopy(item.get("clitic_pos_candidates", [])),
        "syntactic_role": None,
        "syntax_status": None,
        "syntax_reason": None,
    }

    if kind != "word":
        base["syntax_status"] = "not_applicable"
        return base

    key = token.casefold()
    if has_clauses:
        base["syntax_status"] = "deferred"
        base["syntax_reason"] = "compound_clause_mapping_deferred"
        return base
    if parser_status not in {"parsed", "partial"}:
        base["syntax_status"] = "deferred"
        base["syntax_reason"] = "parser_status_not_supported"
        return base
    if source_counts.get(key, 0) != 1:
        base["syntax_status"] = "deferred"
        base["syntax_reason"] = "repeated_source_token"
        return base

    matched_roles = [
        role_name
        for role_name, counts in role_counts.items()
        if counts.get(key, 0) > 0
    ]
    total_observations = sum(
        counts.get(key, 0) for counts in role_counts.values()
    ) + unresolved_counts.get(key, 0)

    if total_observations > 1:
        base["syntax_status"] = "deferred"
        base["syntax_reason"] = "ambiguous_parser_token_mapping"
    elif len(matched_roles) == 1:
        base["syntactic_role"] = matched_roles[0]
        base["syntax_status"] = "mapped"
    elif unresolved_counts.get(key, 0) == 1:
        base["syntax_status"] = "unresolved"
        base["syntax_reason"] = "parser_reports_token_unresolved"
    else:
        base["syntax_status"] = "not_observed"
        base["syntax_reason"] = "parser_has_no_observation_for_token"
    return base


def build_context_snapshot(
    analysis: dict[str, Any],
    parse_result: dict[str, Any],
) -> dict[str, Any]:
    """Combine existing analyzer/POS output and parser output without inference."""
    if not isinstance(analysis, dict) or not isinstance(analysis.get("tokens"), list):
        raise ContextSnapshotError("analysis harus memiliki array tokens")
    if not isinstance(parse_result, dict):
        raise ContextSnapshotError("parse_result harus berupa object")
    roles = parse_result.get("roles")
    if not isinstance(roles, dict):
        raise ContextSnapshotError("parse_result.roles harus berupa object")
    unresolved = parse_result.get("unresolved_tokens", [])
    if not isinstance(unresolved, list) or not all(
        isinstance(value, str) for value in unresolved
    ):
        raise ContextSnapshotError("parse_result.unresolved_tokens harus berupa array teks")

    source_tokens = analysis["tokens"]
    for index, item in enumerate(source_tokens):
        if not isinstance(item, dict) or not isinstance(item.get("token"), str):
            raise ContextSnapshotError(
                f"analysis.tokens[{index}] harus memiliki token berupa teks"
            )

    parser_status = parse_result.get("status")
    has_clauses = "clauses" in parse_result
    source_words = [
        item["token"] for item in source_tokens
        if item.get("kind", "word") == "word"
    ]
    source_counts = _casefold_counts(source_words)

    role_counts: dict[str, dict[str, int]] = {}
    for field, role_name in _ROLE_FIELDS:
        values = _collect_role_tokens(roles.get(field, []))
        role_counts[role_name] = _casefold_counts(values)
    unresolved_counts = _casefold_counts(unresolved)

    token_results = [
        _token_snapshot(
            index,
            item,
            source_counts,
            role_counts,
            unresolved_counts,
            parser_status,
            has_clauses,
        )
        for index, item in enumerate(source_tokens)
    ]

    syntax_states = {
        item["syntax_status"]
        for item in token_results
        if item["kind"] == "word"
    }
    if "deferred" in syntax_states:
        status = "deferred"
    elif parser_status == "partial" or syntax_states.intersection(
        {"unresolved", "not_observed"}
    ):
        status = "partial"
    else:
        status = "assembled"

    return {
        "status": status,
        "normalized_text": deepcopy(analysis.get("normalized_text")),
        "parser_status": parser_status,
        "tokens": token_results,
        "parser_result": deepcopy(parse_result),
    }

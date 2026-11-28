"""Orchestrate contextual sense processing per token occurrence.

This layer composes existing read-only components. It does not alter analyzer,
POS, parser, Concept Layer, evidence generation, or selector behavior.
"""
from __future__ import annotations

from typing import Any

from tools.concept_sense_adapter import map_sense_candidates_to_concepts
from tools.context_evidence_generator import generate_context_evidence
from tools.contextual_sense_selector import select_contextual_sense


class ContextualSenseIntegrationError(ValueError):
    """Input does not satisfy the orchestration contract."""


def _collect_parser_strings(value: Any) -> list[str]:
    found: list[str] = []
    if isinstance(value, str):
        if value.strip():
            found.append(value)
    elif isinstance(value, list):
        for item in value:
            found.extend(_collect_parser_strings(item))
    elif isinstance(value, dict):
        for key in ("adverb", "preposition", "phrase"):
            if key in value:
                found.extend(_collect_parser_strings(value[key]))
    return found


def _parser_observed_tokens(parse_result: dict[str, Any]) -> list[str]:
    roles = parse_result.get("roles", {})
    if not isinstance(roles, dict):
        raise ContextualSenseIntegrationError("parse_result.roles harus berupa object")
    values: list[str] = []
    for role in ("subject", "predicate", "object", "adjuncts", "complement"):
        values.extend(_collect_parser_strings(roles.get(role, [])))
    unresolved = parse_result.get("unresolved_tokens", [])
    if not isinstance(unresolved, list):
        raise ContextualSenseIntegrationError(
            "parse_result.unresolved_tokens harus berupa list"
        )
    values.extend(_collect_parser_strings(unresolved))
    return values


def _deferred_record(
    token_index: int,
    token: str,
    mapped_candidates: list[dict[str, Any]],
    reason: str,
) -> dict[str, Any]:
    return {
        "token_index": token_index,
        "token": token,
        "candidate_senses": mapped_candidates,
        "concept_mappings": [
            {
                "sense_id": item["sense_id"],
                "concepts": list(item.get("concepts", [])),
                "mapping_status": item.get("mapping_status"),
            }
            for item in mapped_candidates
        ],
        "observations": None,
        "evidence": [],
        "evidence_status": "not_run",
        "selection": None,
        "orchestration_status": "deferred",
        "defer_reason": reason,
    }


def orchestrate_contextual_senses(
    analysis: dict[str, Any],
    parse_result: dict[str, Any],
    concept_layer: dict[str, list[dict[str, Any]]],
    context_rules: list[dict[str, Any]],
) -> dict[str, Any]:
    """Run adapter, evidence generator, and selector independently per token.

    analysis must be the existing analyzer output after lexical POS tagging
    and contextual POS processing. parse_result must be its parser output.
    """
    if not isinstance(analysis, dict) or not isinstance(analysis.get("tokens"), list):
        raise ContextualSenseIntegrationError("analysis harus memiliki array tokens")
    if not isinstance(parse_result, dict):
        raise ContextualSenseIntegrationError("parse_result harus berupa object")
    if not isinstance(concept_layer, dict):
        raise ContextualSenseIntegrationError("concept_layer harus berupa object")
    if not isinstance(context_rules, list):
        raise ContextualSenseIntegrationError("context_rules harus berupa list")

    tokens = analysis["tokens"]
    source_words: dict[str, int] = {}
    for item in tokens:
        if not isinstance(item, dict):
            raise ContextualSenseIntegrationError("setiap token harus berupa object")
        if item.get("kind") == "word":
            value = item.get("token")
            if not isinstance(value, str) or not value.strip():
                raise ContextualSenseIntegrationError("token kata harus memiliki teks")
            key = value.casefold()
            source_words[key] = source_words.get(key, 0) + 1

    parser_status = parse_result.get("status")
    has_clauses = "clauses" in parse_result
    parser_tokens = _parser_observed_tokens(parse_result)
    parser_counts: dict[str, int] = {}
    for value in parser_tokens:
        key = value.casefold()
        parser_counts[key] = parser_counts.get(key, 0) + 1
    unresolved_values = _collect_parser_strings(parse_result.get("unresolved_tokens", []))
    unresolved_set = {value.casefold() for value in unresolved_values}

    results: list[dict[str, Any]] = []
    for token_index, item in enumerate(tokens):
        token = item["token"]
        if item.get("kind") != "word":
            results.append({
                "token_index": token_index,
                "token": token,
                "candidate_senses": [],
                "concept_mappings": [],
                "observations": None,
                "evidence": [],
                "evidence_status": "not_applicable",
                "selection": None,
                "orchestration_status": "not_applicable",
                "defer_reason": None,
            })
            continue

        candidates = item.get("candidates", [])
        if not isinstance(candidates, list):
            raise ContextualSenseIntegrationError(
                f"tokens[{token_index}].candidates harus berupa list"
            )
        mapped = map_sense_candidates_to_concepts(candidates, concept_layer)

        reason = None
        if has_clauses:
            reason = "compound_clause_context_deferred"
        elif parser_status not in {"parsed", "partial"}:
            reason = "parser_status_not_usable"
        elif source_words.get(token.casefold(), 0) != 1:
            reason = "repeated_surface_form_mapping_ambiguous"
        elif parser_counts.get(token.casefold(), 0) != 1:
            reason = "parser_token_mapping_unavailable_or_ambiguous"
        elif token.casefold() in unresolved_set:
            reason = "target_token_unresolved_by_parser"

        sense_ids = [entry["sense_id"] for entry in mapped]
        if reason is None and len(sense_ids) != len(set(sense_ids)):
            reason = "duplicate_sense_candidates"

        if reason is not None:
            results.append(_deferred_record(token_index, token, mapped, reason))
            continue

        generated = generate_context_evidence(mapped, parse_result, context_rules)
        selection = select_contextual_sense(mapped, generated["evidence"])
        results.append({
            "token_index": token_index,
            "token": token,
            "candidate_senses": mapped,
            "concept_mappings": [
                {
                    "sense_id": entry["sense_id"],
                    "concepts": list(entry.get("concepts", [])),
                    "mapping_status": entry.get("mapping_status"),
                }
                for entry in mapped
            ],
            "observations": generated["observations"],
            "evidence": generated["evidence"],
            "evidence_status": generated["status"],
            "selection": selection,
            "orchestration_status": "processed",
            "defer_reason": None,
        })

    return {
        "status": (
            "completed"
            if all(item["orchestration_status"] in {"processed", "not_applicable"} for item in results)
            else "partial"
        ),
        "results": results,
    }

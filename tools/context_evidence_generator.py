"""Generate auditable, rule-based evidence for contextual sense selection.

This module does not select senses and does not modify parser or lexical data.
"""
from __future__ import annotations

import re
from typing import Any


class ContextEvidenceGeneratorError(ValueError):
    """Input data does not satisfy the context evidence contract."""


_RULE_ID_RE = re.compile(r"^CE[0-9]{6,}$")
_STATUSES = {"proposed", "reviewed", "rejected"}
_POLARITIES = {"supports", "contradicts"}
_STRENGTHS = {"weak", "strong"}
_ROLES = {"subject", "predicate", "object", "adjuncts", "complement"}
_RULE_FIELDS = {
    "rule_id",
    "status",
    "target_sense_id",
    "conditions",
    "polarity",
    "strength",
    "source",
    "rationale",
}


def _nonempty_text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ContextEvidenceGeneratorError(f"{label} harus berupa teks nonkosong")
    return value


def _collect_strings(value: Any) -> list[str]:
    """Collect visible token strings from parser role structures."""
    found: list[str] = []
    if isinstance(value, str):
        if value.strip():
            found.append(value)
    elif isinstance(value, list):
        for item in value:
            found.extend(_collect_strings(item))
    elif isinstance(value, dict):
        for key in ("adverb", "preposition", "phrase"):
            if key in value:
                found.extend(_collect_strings(value[key]))
    return found


def _validate_condition(condition: Any, index: int) -> dict[str, str]:
    label = f"conditions[{index}]"
    if not isinstance(condition, dict):
        raise ContextEvidenceGeneratorError(f"{label} harus berupa object")
    kind = condition.get("type")
    if kind == "token_present":
        if set(condition) != {"type", "value"}:
            raise ContextEvidenceGeneratorError(
                f"{label} token_present harus memiliki type dan value saja"
            )
        return {
            "type": kind,
            "value": _nonempty_text(condition.get("value"), f"{label}.value"),
        }
    if kind == "role_contains":
        if set(condition) != {"type", "role", "value"}:
            raise ContextEvidenceGeneratorError(
                f"{label} role_contains harus memiliki type, role, dan value saja"
            )
        role = _nonempty_text(condition.get("role"), f"{label}.role")
        if role not in _ROLES:
            raise ContextEvidenceGeneratorError(
                f"{label}.role tidak didukung: {role}"
            )
        return {
            "type": kind,
            "role": role,
            "value": _nonempty_text(condition.get("value"), f"{label}.value"),
        }
    raise ContextEvidenceGeneratorError(f"{label}.type tidak dikenal: {kind}")


def _validate_rule(rule: Any, index: int) -> dict[str, Any]:
    label = f"context_rules[{index}]"
    if not isinstance(rule, dict):
        raise ContextEvidenceGeneratorError(f"{label} harus berupa object")
    if set(rule) != _RULE_FIELDS:
        missing = sorted(_RULE_FIELDS - set(rule))
        extra = sorted(set(rule) - _RULE_FIELDS)
        raise ContextEvidenceGeneratorError(
            f"{label} memiliki field tidak sesuai; missing={missing}, extra={extra}"
        )

    rule_id = _nonempty_text(rule["rule_id"], f"{label}.rule_id")
    if not _RULE_ID_RE.fullmatch(rule_id):
        raise ContextEvidenceGeneratorError(
            f"{label}.rule_id harus berformat CE diikuti minimal enam digit"
        )
    status = rule["status"]
    if status not in _STATUSES:
        raise ContextEvidenceGeneratorError(f"{label}.status tidak dikenal")
    target_sense_id = _nonempty_text(
        rule["target_sense_id"], f"{label}.target_sense_id"
    )
    polarity = rule["polarity"]
    if polarity not in _POLARITIES:
        raise ContextEvidenceGeneratorError(f"{label}.polarity tidak dikenal")
    strength = rule["strength"]
    if strength not in _STRENGTHS:
        raise ContextEvidenceGeneratorError(f"{label}.strength tidak dikenal")
    if not isinstance(rule["conditions"], list) or not rule["conditions"]:
        raise ContextEvidenceGeneratorError(
            f"{label}.conditions harus berupa list nonkosong"
        )
    conditions = [
        _validate_condition(item, condition_index)
        for condition_index, item in enumerate(rule["conditions"])
    ]
    if strength == "strong" and not any(
        item["type"] == "token_present" for item in conditions
    ):
        raise ContextEvidenceGeneratorError(
            f"{label}: aturan strong wajib memiliki kondisi token_present"
        )

    return {
        "rule_id": rule_id,
        "status": status,
        "target_sense_id": target_sense_id,
        "conditions": conditions,
        "polarity": polarity,
        "strength": strength,
        "source": _nonempty_text(rule["source"], f"{label}.source"),
        "rationale": _nonempty_text(rule["rationale"], f"{label}.rationale"),
    }


def generate_context_evidence(
    sense_candidates: list[dict[str, Any]],
    parse_result: dict[str, Any],
    context_rules: list[dict[str, Any]],
) -> dict[str, Any]:
    """Extract observations and emit evidence from reviewed context rules.

    sense_candidates follows the per-sense records returned by the concept
    sense adapter. A rule matches only when every condition matches. This
    function never selects a sense or assigns a final ambiguous/unresolved
    status.
    """
    if not isinstance(sense_candidates, list):
        raise ContextEvidenceGeneratorError("sense_candidates harus berupa list")
    if not isinstance(parse_result, dict):
        raise ContextEvidenceGeneratorError("parse_result harus berupa object")
    if not isinstance(context_rules, list):
        raise ContextEvidenceGeneratorError("context_rules harus berupa list")

    candidates_by_sense: dict[str, list[str]] = {}
    for index, candidate in enumerate(sense_candidates):
        label = f"sense_candidates[{index}]"
        if not isinstance(candidate, dict):
            raise ContextEvidenceGeneratorError(f"{label} harus berupa object")
        sense_id = _nonempty_text(candidate.get("sense_id"), f"{label}.sense_id")
        concepts = candidate.get("concepts", [])
        if not isinstance(concepts, list):
            raise ContextEvidenceGeneratorError(f"{label}.concepts harus berupa list")
        concept_ids: list[str] = []
        for concept_index, concept in enumerate(concepts):
            if not isinstance(concept, dict):
                raise ContextEvidenceGeneratorError(
                    f"{label}.concepts[{concept_index}] harus berupa object"
                )
            concept_id = _nonempty_text(
                concept.get("concept_id"),
                f"{label}.concepts[{concept_index}].concept_id",
            )
            if concept_id not in concept_ids:
                concept_ids.append(concept_id)
        candidates_by_sense.setdefault(sense_id, [])
        for concept_id in concept_ids:
            if concept_id not in candidates_by_sense[sense_id]:
                candidates_by_sense[sense_id].append(concept_id)

    parser_status = parse_result.get("status", "unknown")
    if not isinstance(parser_status, str) or not parser_status.strip():
        parser_status = "unknown"
    raw_roles = parse_result.get("roles", {})
    if not isinstance(raw_roles, dict):
        raise ContextEvidenceGeneratorError("parse_result.roles harus berupa object")

    role_tokens: dict[str, list[str]] = {}
    observed_tokens: list[str] = []
    for role in sorted(_ROLES):
        values = _collect_strings(raw_roles.get(role, []))
        role_tokens[role] = list(dict.fromkeys(values))
        for token in role_tokens[role]:
            if token not in observed_tokens:
                observed_tokens.append(token)

    unresolved = parse_result.get("unresolved_tokens", [])
    if not isinstance(unresolved, list):
        raise ContextEvidenceGeneratorError(
            "parse_result.unresolved_tokens harus berupa list"
        )
    unresolved_tokens = _collect_strings(unresolved)
    for token in unresolved_tokens:
        if token not in observed_tokens:
            observed_tokens.append(token)

    observations = {
        "parser_status": parser_status,
        "roles": role_tokens,
        "unresolved_tokens": list(dict.fromkeys(unresolved_tokens)),
        "observed_tokens": observed_tokens,
    }

    validated_rules = [
        _validate_rule(rule, index)
        for index, rule in enumerate(context_rules)
    ]
    seen_rule_ids: set[str] = set()
    for rule in validated_rules:
        if rule["rule_id"] in seen_rule_ids:
            raise ContextEvidenceGeneratorError(
                f"rule_id duplikat: {rule['rule_id']}"
            )
        seen_rule_ids.add(rule["rule_id"])

    evidence: list[dict[str, Any]] = []
    for rule in validated_rules:
        if rule["status"] != "reviewed":
            continue
        sense_id = rule["target_sense_id"]
        if sense_id not in candidates_by_sense:
            continue

        matched_conditions: list[dict[str, str]] = []
        all_match = True
        for condition in rule["conditions"]:
            value = condition["value"]
            if condition["type"] == "token_present":
                observed = {
                    token.casefold() for token in observations["observed_tokens"]
                }
                matched = value.casefold() in observed
            else:
                observed = {
                    token.casefold() for token in role_tokens[condition["role"]]
                }
                matched = (
                    parser_status in {"parsed", "partial"}
                    and value.casefold() in observed
                )
            if not matched:
                all_match = False
                break
            matched_conditions.append(dict(condition))

        if all_match:
            evidence.append({
                "sense_id": sense_id,
                "concept_ids": list(candidates_by_sense[sense_id]),
                "polarity": rule["polarity"],
                "strength": rule["strength"],
                "source": rule["source"],
                "rule_id": rule["rule_id"],
                "rationale": rule["rationale"],
                "matched_conditions": matched_conditions,
                "token_spans": [],
            })

    notes: list[str] = []
    if parser_status == "partial":
        notes.append(
            "Parser partial: hanya observasi yang tersedia digunakan; unresolved_tokens bukan struktur terkonfirmasi."
        )
    elif parser_status != "parsed":
        notes.append(
            "Parser unresolved atau status tidak dikenal: kondisi berbasis role tidak digunakan."
        )
    if not evidence:
        notes.append(
            "Tidak ada aturan reviewed yang cocok; hasil ini bukan bukti bahwa sense kandidat salah."
        )

    return {
        "observations": observations,
        "evidence": evidence,
        "status": "evidence_found" if evidence else "no_evidence",
        "notes": notes,
    }

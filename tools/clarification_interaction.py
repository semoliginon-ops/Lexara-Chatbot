"""Safe presentation and response recording for clarification sessions.

This module uses validated lexical sense definitions and does not interpret
free-text answers or manage persistent/runtime dialogue state.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Any


def _cannot_present(reason: str) -> dict[str, Any]:
    return {
        "status": "cannot_present_safely",
        "reason": reason,
        "prompt": None,
        "session": None,
    }


def _valid_index(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def prepare_clarification_prompt(
    plan: dict[str, Any],
    snapshot: dict[str, Any],
    session_id: str,
) -> dict[str, Any]:
    """Prepare one neutral prompt only from validated lexical sense definitions."""
    if not isinstance(plan, dict) or plan.get("decision") != "ask":
        return _cannot_present("planner_did_not_request_clarification")
    focus = plan.get("focus")
    if not isinstance(focus, dict):
        return _cannot_present("missing_or_invalid_focus")
    if not isinstance(session_id, str) or not session_id.strip():
        return _cannot_present("invalid_session_id")
    if not isinstance(snapshot, dict) or not isinstance(snapshot.get("tokens"), list):
        return _cannot_present("invalid_snapshot")

    parent = focus.get("parent_candidate_ref")
    refs = focus.get("sense_refs")
    if (
        not isinstance(parent, dict)
        or parent.get("source_field") != "lexical_candidates"
        or not _valid_index(parent.get("token_index"))
        or not _valid_index(parent.get("candidate_index"))
        or not isinstance(refs, list)
        or len(refs) < 2
    ):
        return _cannot_present("sense_level_focus_required")

    token_index = parent["token_index"]
    candidate_index = parent["candidate_index"]
    tokens = snapshot["tokens"]
    if token_index >= len(tokens) or not isinstance(tokens[token_index], dict):
        return _cannot_present("token_reference_not_found")
    token_item = tokens[token_index]
    token_text = token_item.get("token")
    if token_item.get("kind", "word") != "word" or not isinstance(token_text, str):
        return _cannot_present("token_not_presentable")

    lexical = token_item.get("lexical_candidates")
    if not isinstance(lexical, list) or candidate_index >= len(lexical):
        return _cannot_present("candidate_reference_not_found")
    candidate = lexical[candidate_index]
    if not isinstance(candidate, dict) or not isinstance(candidate.get("entry"), dict):
        return _cannot_present("candidate_entry_missing")
    senses = candidate["entry"].get("senses")
    if not isinstance(senses, list):
        return _cannot_present("sense_inventory_missing")

    choices: list[dict[str, Any]] = []
    seen_refs: list[dict[str, Any]] = []
    seen_labels: set[str] = set()
    for ref in refs:
        if not isinstance(ref, dict):
            return _cannot_present("invalid_sense_reference")
        if (
            ref.get("source_field") != "lexical_candidates"
            or ref.get("token_index") != token_index
            or ref.get("candidate_index") != candidate_index
            or not _valid_index(ref.get("sense_index"))
            or not isinstance(ref.get("sense_id"), str)
        ):
            return _cannot_present("sense_reference_mismatch")
        if any(ref == previous for previous in seen_refs):
            return _cannot_present("duplicate_sense_reference")
        seen_refs.append(ref)
        sense_index = ref["sense_index"]
        if sense_index >= len(senses):
            return _cannot_present("sense_index_not_found")
        sense = senses[sense_index]
        if not isinstance(sense, dict) or sense.get("sense_id") != ref["sense_id"]:
            return _cannot_present("sense_id_mismatch")
        definition = sense.get("definition")
        if not isinstance(definition, str) or not definition.strip():
            return _cannot_present("sense_definition_missing")
        label = definition.strip()
        normalized_label = label.casefold()
        if normalized_label in seen_labels:
            return _cannot_present("sense_definitions_not_distinguishable")
        seen_labels.add(normalized_label)
        choices.append({
            "choice_key": f"option_{len(choices) + 1}",
            "label": label,
            "sense_ref": deepcopy(ref),
        })

    prompt = {
        "text": f'Pada bagian "{token_text}", makna yang kamu maksud yang mana?',
        "choices": [
            {"key": choice["choice_key"], "label": choice["label"]}
            for choice in choices
        ],
        "allow_free_text": True,
        "allow_decline": True,
    }
    session = {
        "session_id": session_id,
        "status": "presented",
        "planner_focus": deepcopy(focus),
        "choices": choices,
        "response": None,
    }
    return {
        "status": "presented",
        "reason": "validated_sense_definitions",
        "prompt": prompt,
        "session": session,
    }


def record_clarification_response(
    session: dict[str, Any],
    response: Any,
) -> dict[str, Any]:
    """Record one explicit response without interpreting free text."""
    if not isinstance(session, dict):
        return {"status": "invalid_response", "session": None}
    result = deepcopy(session)
    if result.get("status") != "presented" or not isinstance(result.get("choices"), list):
        return {"status": "invalid_response", "session": result}

    if not isinstance(response, dict):
        result["status"] = "invalid_response"
        result["response"] = None
        return {"status": "invalid_response", "session": result}

    response_type = response.get("type")
    if response_type == "choice":
        key = response.get("choice_key")
        matching = [
            choice for choice in result["choices"]
            if isinstance(choice, dict) and choice.get("choice_key") == key
        ]
        if (
            len(matching) != 1
            or not isinstance(matching[0].get("sense_ref"), dict)
        ):
            result["status"] = "invalid_response"
            result["response"] = None
            return {"status": "invalid_response", "session": result}
        choice = matching[0]
        result["status"] = "answered_choice"
        result["response"] = {
            "type": "choice",
            "choice_key": key,
            "sense_ref": deepcopy(choice["sense_ref"]),
        }
        return {"status": "answered_choice", "session": result}

    if response_type == "free_text":
        text = response.get("text")
        if not isinstance(text, str) or not text.strip():
            result["status"] = "invalid_response"
            result["response"] = None
            return {"status": "invalid_response", "session": result}
        result["status"] = "answered_free_text"
        result["response"] = {
            "type": "free_text",
            "text": text,
            "completeness": "unknown",
        }
        return {"status": "answered_free_text", "session": result}

    if response_type == "decline":
        result["status"] = "declined"
        result["response"] = {"type": "decline"}
        return {"status": "declined", "session": result}

    if response_type == "no_response":
        result["status"] = "no_response"
        result["response"] = {"type": "no_response"}
        return {"status": "no_response", "session": result}

    if response_type == "cancel":
        result["status"] = "cancelled"
        result["response"] = {"type": "cancel"}
        return {"status": "cancelled", "session": result}

    result["status"] = "invalid_response"
    result["response"] = None
    return {"status": "invalid_response", "session": result}

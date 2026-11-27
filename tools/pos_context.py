"""Conservative local-context POS disambiguation for Indonesian text."""
from __future__ import annotations
from typing import Any

_ASPECT_OR_MODAL = {"sedang", "akan", "telah", "sudah", "lagi"}
_PREPOSITIONS = {"di", "ke", "dari", "pada", "dalam", "untuk"}
_DEMONSTRATIVES = {"ini", "itu", "tersebut"}


def _labels(token: dict[str, Any]) -> list[str]:
    labels = token.get("pos", [])
    if not isinstance(labels, list) or not all(
        isinstance(label, str) and label for label in labels
    ):
        raise ValueError("field pos setiap token harus berupa array teks")
    return list(dict.fromkeys(labels))


def disambiguate_pos_context(analysis: dict[str, Any]) -> dict[str, Any]:
    """Add conservative context decisions without overwriting lexical POS."""
    if not isinstance(analysis, dict):
        raise TypeError("analysis harus berupa dictionary hasil tag_pos")
    tokens = analysis.get("tokens")
    if not isinstance(tokens, list):
        raise ValueError("analysis harus memiliki array tokens")

    source_tokens = []
    for item in tokens:
        if not isinstance(item, dict):
            raise ValueError("setiap token harus berupa objek")
        source_tokens.append(dict(item))

    result_tokens = []
    for index, item in enumerate(source_tokens):
        updated = dict(item)
        token = item.get("token")
        if not isinstance(token, str):
            raise ValueError("setiap token harus memiliki field token berupa teks")

        candidates = _labels(item)
        status = item.get("pos_status", "unknown")
        evidence: list[dict[str, str]] = []
        context_pos = None

        if status == "not_applicable":
            context_status = "not_applicable"
        elif status == "requires_morphology":
            context_status = "requires_morphology"
        elif not candidates:
            context_status = "unknown"
        elif len(candidates) == 1:
            context_pos = candidates[0]
            context_status = "unambiguous"
        else:
            previous = source_tokens[index - 1] if index > 0 else None
            following = source_tokens[index + 1] if index + 1 < len(source_tokens) else None
            previous_text = previous.get("token", "").casefold() if previous else ""
            following_text = following.get("token", "").casefold() if following else ""
            following_pos = _labels(following) if following else []

            if previous_text in _ASPECT_OR_MODAL and "VERB" in candidates:
                evidence.append({"rule": "aspect_or_modal_before", "pos": "VERB", "cue_token": previous_text})
            if previous_text in _PREPOSITIONS and "NOUN" in candidates:
                evidence.append({"rule": "preposition_before", "pos": "NOUN", "cue_token": previous_text})
            if following_text in _DEMONSTRATIVES and "NOUN" in candidates:
                evidence.append({"rule": "demonstrative_after", "pos": "NOUN", "cue_token": following_text})

            if previous_text in {"dan", "serta", "maupun"} and index >= 2:
                left_conjunct = source_tokens[index - 2]
                left_labels = _labels(left_conjunct)
                shared_labels = set(candidates).intersection(left_labels)
                if len(shared_labels) == 1:
                    evidence.append({
                        "rule": "coordination_with_previous_conjunct",
                        "pos": next(iter(shared_labels)),
                        "cue_token": left_conjunct.get("token", "").casefold(),
                    })

            if token.casefold() == "tetap" and following and "ADV" in candidates and "VERB" in following_pos:
                evidence.append({"rule": "tetap_before_verb", "pos": "ADV", "cue_token": following_text})

            if token.casefold() == "bisa" and following:
                if "VERB" in following_pos and "VERB" in candidates:
                    evidence.append({"rule": "bisa_before_verb", "pos": "VERB", "cue_token": following_text})
                elif "NOUN" in following_pos and "NOUN" in candidates:
                    evidence.append({"rule": "bisa_before_noun", "pos": "NOUN", "cue_token": following_text})

            supported = {item["pos"] for item in evidence}
            if len(supported) == 1:
                context_pos = next(iter(supported))
                context_status = "selected_by_context"
            else:
                context_status = "ambiguous"

        updated["context_pos"] = context_pos
        updated["pos_context_status"] = context_status
        updated["pos_context_evidence"] = evidence
        result_tokens.append(updated)

    result = dict(analysis)
    result["tokens"] = result_tokens
    result["pos_contextual_disambiguation"] = True
    result["pos_context_method"] = "conservative_local_rules_v1"
    return result

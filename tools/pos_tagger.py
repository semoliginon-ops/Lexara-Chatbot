"""Lexicon-based POS tagging that preserves lexical ambiguity."""
from __future__ import annotations

from typing import Any


def _sense_pos(entry: dict[str, Any]) -> list[dict[str, Any]]:
    """Return POS labels per sense, falling back to the entry-level POS."""
    entry_pos = entry.get("pos", [])
    if not isinstance(entry_pos, list):
        raise ValueError("field pos pada entri harus berupa array")

    senses = entry.get("senses", [])
    if not isinstance(senses, list):
        raise ValueError("field senses pada entri harus berupa array")

    result = []
    for sense in senses:
        if not isinstance(sense, dict):
            raise ValueError("setiap sense harus berupa objek")
        sense_pos = sense.get("pos", entry_pos)
        if isinstance(sense_pos, str):
            sense_pos = [sense_pos]
        if not isinstance(sense_pos, list) or not all(
            isinstance(label, str) and label for label in sense_pos
        ):
            raise ValueError("POS pada sense harus berupa teks atau array teks")
        result.append({
            "sense_id": sense.get("sense_id"),
            "pos": list(dict.fromkeys(sense_pos)),
        })
    return result


def tag_pos(analysis: dict[str, Any]) -> dict[str, Any]:
    """Add dictionary POS candidates to analyze_text output.

    This is lexical POS identification only. It does not use sentence context
    and never chooses one POS or sense when multiple candidates are present.
    """
    if not isinstance(analysis, dict):
        raise TypeError("analysis harus berupa dictionary hasil analyze_text")
    tokens = analysis.get("tokens")
    if not isinstance(tokens, list):
        raise ValueError("analysis harus memiliki array tokens")

    tagged_tokens = []
    for item in tokens:
        if not isinstance(item, dict):
            raise ValueError("setiap token harus berupa objek")
        updated = dict(item)
        candidates = item.get("candidates", [])
        if not isinstance(candidates, list):
            raise ValueError("candidates harus berupa array")

        pos_candidates = []
        for candidate in candidates:
            if not isinstance(candidate, dict):
                raise ValueError("setiap candidate harus berupa objek")
            entry = candidate.get("entry")
            if not isinstance(entry, dict):
                raise ValueError("candidate harus menyertakan entry kamus")
            pos = entry.get("pos", [])
            if not isinstance(pos, list) or not all(
                isinstance(label, str) and label for label in pos
            ):
                raise ValueError("field pos pada entri harus berupa array teks")
            match_type = candidate.get("match_type")
            # A recorded derivative may change POS (makan -> makanan).
            # Do not copy the lemma POS onto it without morphological evidence.
            inherited_pos = [] if match_type == "derived_form" else list(dict.fromkeys(pos))
            pos_candidates.append({
                "entry_id": candidate.get("entry_id"),
                "lemma": candidate.get("lemma"),
                "match_type": match_type,
                "pos": inherited_pos,
                "senses": [] if match_type == "derived_form" else _sense_pos(entry),
            })

        all_labels = []
        for candidate in pos_candidates:
            for label in candidate["pos"]:
                if label not in all_labels:
                    all_labels.append(label)

        updated["pos_candidates"] = pos_candidates
        updated["pos"] = all_labels
        has_unresolved_derivative = any(
            candidate.get("match_type") == "derived_form"
            for candidate in candidates
        )
        updated["pos_status"] = (
            "identified" if all_labels else
            "requires_morphology" if has_unresolved_derivative else
            "unknown" if item.get("kind") == "word" else
            "not_applicable"
        )
        tagged_tokens.append(updated)

    result = dict(analysis)
    result["tokens"] = tagged_tokens
    result["pos_method"] = "lexicon"
    result["pos_contextual_disambiguation"] = False
    return result

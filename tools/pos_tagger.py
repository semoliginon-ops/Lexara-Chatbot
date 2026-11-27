"""Lexicon-based POS tagging that preserves lexical ambiguity."""
from __future__ import annotations

from typing import Any

from tools.pos_supplement import supplementary_pos


_VERBAL_MORPHOLOGY_RULES = (
    "prefix_meN", "prefix_di", "nasal_restoration_m",
    "nasal_retention_meny",
)


def _morphological_verbal_pos(morphology_candidates: list[dict[str, Any]]) -> list[str]:
    """Return VERB only when every validated analysis supports verbal morphology."""
    if not morphology_candidates:
        return []
    for morphology in morphology_candidates:
        rule = morphology.get("rule", "")
        is_verbal_rule = (
            rule == "prefix_meN" or rule.startswith("prefix_meN+")
            or rule == "prefix_di" or rule.startswith("prefix_di+")
            or (rule == "prefix_ber" and morphology.get("recorded_derived_form") is True)
            or rule.startswith("nasal_restoration_m")
            or rule.startswith("nasal_retention_meny")
        )
        if not is_verbal_rule:
            return []
        matches = morphology.get("candidates", [])
        if not matches:
            return []
        for match in matches:
            entry = match.get("entry", {})
            labels = entry.get("pos", []) if isinstance(entry, dict) else []
            if not isinstance(labels, list) or "VERB" not in labels:
                return []
    return ["VERB"]


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
            # A derived form may change POS. Never inherit the lemma label;
            # use only an explicitly audited surface-form annotation.
            if match_type == "derived_form":
                derived_pos_map = entry.get("derived_forms_pos", {})
                if not isinstance(derived_pos_map, dict):
                    raise ValueError("derived_forms_pos harus berupa objek")
                inherited_pos = derived_pos_map.get(candidate.get("matched_form"), [])
                if (
                    not isinstance(inherited_pos, list)
                    or not all(isinstance(label, str) and label for label in inherited_pos)
                ):
                    raise ValueError("POS bentuk turunan harus berupa array label teks")
                inherited_pos = list(dict.fromkeys(inherited_pos))
            else:
                inherited_pos = list(dict.fromkeys(pos))
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

        has_unresolved_derivative = any(
            candidate.get("match_type") == "derived_form"
            for candidate in candidates
        )

        morphology_candidates = item.get("morphology_candidates", [])
        clitic_pos_candidates = []
        for morphology in morphology_candidates:
            clitic = morphology.get("clitic")
            if clitic not in {"ku", "mu", "nya"}:
                continue
            host_pos = []
            for match in morphology.get("candidates", []):
                entry = match.get("entry", {})
                if not isinstance(entry, dict):
                    continue
                if match.get("match_type") == "derived_form":
                    derived_map = entry.get("derived_forms_pos", {})
                    labels = derived_map.get(match.get("matched_form"), [])
                    if not isinstance(labels, list):
                        labels = []
                else:
                    labels = entry.get("pos", [])
                for label in labels:
                    if isinstance(label, str) and label and label not in host_pos:
                        host_pos.append(label)
            clitic_pos_candidates.append({
                "base_form": morphology.get("base_form"),
                "clitic": clitic,
                "host_pos": host_pos,
                "clitic_pos": ["PRON"],
                "combined_pos": [
                    {"host": host_label, "clitic": "PRON"}
                    for host_label in host_pos
                ],
                "function_candidates": ["possessive", "object"],
                "function_status": "unresolved",
            })

        morphology_labels = _morphological_verbal_pos(morphology_candidates)

        # Use the small audited supplement only when the dictionary has no
        # POS candidate and the token is not an unresolved derived form.
        supplement_label = None
        if not all_labels and not candidates and item.get("kind") == "word":
            supplement_label = supplementary_pos(item.get("token", ""))

        if all_labels:
            updated["pos_source"] = "dictionary"
        elif morphology_labels:
            all_labels = morphology_labels
            updated["pos_source"] = "morphology"
        elif supplement_label:
            all_labels = [supplement_label]
            updated["pos_source"] = "supplement"
        elif has_unresolved_derivative:
            updated["pos_source"] = "requires_morphology"
        else:
            updated["pos_source"] = "unknown" if item.get("kind") == "word" else "not_applicable"

        updated["pos_candidates"] = pos_candidates
        updated["clitic_pos_candidates"] = clitic_pos_candidates
        updated["pos"] = all_labels
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

"""Resolusi konservatif kandidat semantic role dengan bukti konteks eksplisit.

Modul ini tidak menebak kelas semantis entitas dari ejaan kata. Ia hanya
menggunakan bukti konteks terstruktur yang diberikan oleh lapisan konteks lain.
Kandidat dipilih hanya jika satu frame mendapat dukungan kuat dan semua frame
alternatif mendapat bukti kuat yang menentangnya untuk argumen pembeda.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Any


def resolve_semantic_role_candidates(
    mapping_result: dict[str, Any],
    context_evidence: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Resolve mapper ambiguity only when contextual evidence is decisive.

    Evidence fields:
      frame_id, argument_id, semantic_role,
      polarity ("supports" | "contradicts"),
      strength ("strong" | "weak"), source (non-empty string).
    Weak or unmatched evidence is retained in the audit but never selects.
    """
    if not isinstance(mapping_result, dict):
        raise TypeError("mapping_result harus berupa dictionary")
    if context_evidence is None:
        context_evidence = []
    if not isinstance(context_evidence, list):
        raise TypeError("context_evidence harus berupa array")

    result = deepcopy(mapping_result)
    candidates = result.get("candidates", [])
    if result.get("status") != "ambiguous":
        result["context_resolution"] = {
            "status": "not_needed",
            "reason": "mapping_not_ambiguous",
            "used_evidence": [],
            "ignored_evidence": [],
        }
        return result
    if not isinstance(candidates, list) or len(candidates) < 2:
        raise ValueError("hasil ambiguous harus memiliki minimal dua kandidat")

    normalized_evidence = []
    ignored = []
    for index, evidence in enumerate(context_evidence):
        if not isinstance(evidence, dict):
            raise TypeError(f"bukti konteks ke-{index} harus berupa dictionary")
        required = ("frame_id", "argument_id", "semantic_role", "polarity", "strength", "source")
        if any(key not in evidence for key in required):
            raise ValueError(f"bukti konteks ke-{index} kehilangan field wajib")
        if evidence["polarity"] not in {"supports", "contradicts"}:
            raise ValueError(f"polarity bukti konteks ke-{index} tidak valid")
        if evidence["strength"] not in {"strong", "weak"}:
            raise ValueError(f"strength bukti konteks ke-{index} tidak valid")
        if not all(isinstance(evidence[key], str) and evidence[key].strip()
                   for key in ("frame_id", "argument_id", "semantic_role", "source")):
            raise ValueError(f"identitas bukti konteks ke-{index} harus berupa teks nonkosong")
        normalized_evidence.append(dict(evidence))

    candidate_states = {}
    for candidate in candidates:
        if not isinstance(candidate, dict) or not isinstance(candidate.get("frame_id"), str):
            raise ValueError("setiap kandidat harus memiliki frame_id")
        frame_id = candidate["frame_id"]
        if frame_id in candidate_states:
            raise ValueError("frame_id kandidat harus unik")
        arguments = candidate.get("arguments")
        if not isinstance(arguments, list):
            raise ValueError("setiap kandidat harus memiliki array arguments")
        candidate_states[frame_id] = {
            "candidate": candidate,
            "supports": {},
            "contradictions": {},
        }

    for evidence in normalized_evidence:
        state = candidate_states.get(evidence["frame_id"])
        if state is None:
            ignored.append({**evidence, "reason": "unknown_frame"})
            continue
        matching_argument = next(
            (argument for argument in state["candidate"]["arguments"]
             if isinstance(argument, dict)
             and argument.get("argument_id") == evidence["argument_id"]
             and argument.get("semantic_role") == evidence["semantic_role"]),
            None,
        )
        if matching_argument is None:
            ignored.append({**evidence, "reason": "argument_role_mismatch"})
            continue
        if evidence["strength"] != "strong":
            ignored.append({**evidence, "reason": "weak_evidence_not_decisive"})
            continue
        target = "supports" if evidence["polarity"] == "supports" else "contradictions"
        state[target].setdefault(evidence["argument_id"], []).append(evidence)

    # Compare alternatives only on the same argument slot. Evidence about
    # different arguments cannot be combined to manufacture a frame choice.
    argument_ids = {
        argument_id
        for state in candidate_states.values()
        for argument_id in (*state["supports"].keys(), *state["contradictions"].keys())
    }
    decisive_winners = set()
    for argument_id in argument_ids:
        for frame_id, state in candidate_states.items():
            has_support = bool(state["supports"].get(argument_id))
            has_contradiction = bool(state["contradictions"].get(argument_id))
            if not has_support or has_contradiction:
                continue
            alternatives_excluded = all(
                bool(other["contradictions"].get(argument_id))
                and not bool(other["supports"].get(argument_id))
                for other_id, other in candidate_states.items()
                if other_id != frame_id
            )
            if alternatives_excluded:
                decisive_winners.add(frame_id)

    used = [
        evidence
        for state in candidate_states.values()
        for evidence_list in (*state["supports"].values(), *state["contradictions"].values())
        for evidence in evidence_list
    ]
    if len(decisive_winners) == 1:
        selected_id = next(iter(decisive_winners))
        result["candidates"] = [candidate_states[selected_id]["candidate"]]
        result["status"] = "mapped"
        result["reason"] = None
        result["context_resolution"] = {
            "status": "resolved",
            "reason": "one_frame_supported_all_alternatives_excluded",
            "selected_frame_id": selected_id,
            "used_evidence": used,
            "ignored_evidence": ignored,
        }
        result.setdefault("notes", []).append(
            "Satu frame dipilih berdasarkan bukti konteks kuat yang mendukungnya dan menyingkirkan semua alternatif."
        )
        return result

    result["context_resolution"] = {
        "status": "unresolved",
        "reason": (
            "conflicting_evidence"
            if any(state["supports"] and state["contradictions"]
                   for state in candidate_states.values())
            else "insufficient_discriminating_evidence"
        ),
        "selected_frame_id": None,
        "used_evidence": used,
        "ignored_evidence": ignored,
    }
    return result

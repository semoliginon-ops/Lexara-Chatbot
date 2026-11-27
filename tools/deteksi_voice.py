"""Deteksi voice verbal konservatif dari bukti analisis morfologi."""
from __future__ import annotations

from typing import Any


_ACTIVE_NASAL_PREFIXES = (
    "nasal_restoration_meng",
    "nasal_restoration_meny",
    "nasal_restoration_men",
    "nasal_restoration_mem",
)


def _is_verb_candidate(item: dict[str, Any]) -> bool:
    match = item.get("candidates")
    if not isinstance(match, list):
        return False
    for candidate in match:
        if not isinstance(candidate, dict):
            continue
        entry = candidate.get("entry")
        if not isinstance(entry, dict):
            continue
        pos = entry.get("pos")
        if isinstance(pos, list) and "VERB" in pos:
            return True
    return False


def _voice_from_rule(rule: Any) -> str | None:
    if not isinstance(rule, str):
        return None
    if rule == "prefix_di" or rule.startswith("prefix_di+"):
        return "passive"
    if rule == "prefix_meN" or rule.startswith("prefix_meN+"):
        return "active"
    if rule == "prefix_memper" or rule.startswith("prefix_memper+"):
        return "active"
    if any(rule == prefix or rule.startswith(prefix + "+") for prefix in _ACTIVE_NASAL_PREFIXES):
        return "active"
    return None


def detect_voice(morphology_candidates: list[dict[str, Any]]) -> dict[str, Any]:
    """Identify active/passive only from dictionary-validated verbal morphology.

    Di- forms can support a passive reading; meN-/memper- forms can support an
    active reading. Ter-, ber-, zero-marked predicates, and conflicting
    candidates are deliberately not forced into a voice label.
    """
    if not isinstance(morphology_candidates, list):
        raise TypeError("morphology_candidates harus berupa array")

    evidence: list[dict[str, str]] = []
    for item in morphology_candidates:
        if not isinstance(item, dict) or not _is_verb_candidate(item):
            continue
        voice = _voice_from_rule(item.get("rule"))
        if voice is None:
            continue
        base_form = item.get("base_form")
        surface = item.get("surface")
        evidence.append({
            "voice": voice,
            "rule": item["rule"],
            "base_form": base_form if isinstance(base_form, str) else "",
            "surface": surface if isinstance(surface, str) else "",
        })

    voices = {item["voice"] for item in evidence}
    if len(voices) == 1:
        voice = next(iter(voices))
        return {
            "status": "identified",
            "voice": voice,
            "reason": "dictionary_validated_voice_morphology",
            "evidence": evidence,
            "notes": [
                "Label voice didukung oleh pola morfologi yang cocok dengan kandidat lema VERB di kamus.",
                "Hasil ini adalah bukti morfologis, bukan analisis sintaksis lengkap atau jaminan bahwa semua konstruksi memakai voice yang sama.",
            ],
        }
    if len(voices) > 1:
        return {
            "status": "ambiguous",
            "voice": None,
            "reason": "conflicting_voice_candidates",
            "evidence": evidence,
            "notes": [
                "Kandidat morfologi verbal mendukung lebih dari satu voice; sistem tidak memilih salah satunya.",
            ],
        }
    return {
        "status": "unresolved",
        "voice": None,
        "reason": "no_confirmed_voice_morphology",
        "evidence": [],
        "notes": [
            "Tidak ditemukan bukti morfologi verbal yang cukup untuk menetapkan voice. Bentuk ter-, ber-, dan verba tanpa penanda yang dikenali tidak dipaksakan menjadi aktif atau pasif.",
        ],
    }

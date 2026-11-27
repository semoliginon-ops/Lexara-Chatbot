"""Pemetaan konservatif fungsi sintaksis ke semantic role berbasis valensi.

Modul ini adalah lapisan terpisah dari parser. Pemanggil wajib memasok voice
yang telah ditentukan oleh analisis morfologi/konteks; parser v1.9 sendiri
belum menentukan voice secara andal. Hanya voice aktif yang dipetakan saat ini.
Jika beberapa frame cocok, semua kandidat dipertahankan dan status ambiguous.
"""
from __future__ import annotations

from typing import Any


_ROLE_FIELDS = {
    "SUBJ": "subject",
    "OBJ": "object",
    "COMP": "complement",
    "OBL": "adjuncts",
}


def _unresolved(reason: str, note: str) -> dict[str, Any]:
    return {
        "status": "unresolved",
        "reason": reason,
        "sense_id": None,
        "candidates": [],
        "notes": [note],
    }


def _oblique_values(adjuncts: list[Any], realizations: list[dict[str, Any]]) -> list[dict[str, Any]]:
    allowed_prepositions: set[str] = set()
    has_preposition_constraint = False
    for realization in realizations:
        if realization.get("type") != "PP":
            continue
        prepositions = realization.get("prepositions")
        if isinstance(prepositions, list) and prepositions:
            has_preposition_constraint = True
            allowed_prepositions.update(
                value.strip().casefold()
                for value in prepositions
                if isinstance(value, str) and value.strip()
            )

    matched = []
    for adjunct in adjuncts:
        if not isinstance(adjunct, dict):
            continue
        preposition = adjunct.get("preposition")
        phrase = adjunct.get("phrase")
        if not isinstance(preposition, str) or not isinstance(phrase, list):
            continue
        if has_preposition_constraint and preposition.casefold() not in allowed_prepositions:
            continue
        matched.append({
            "preposition": preposition,
            "phrase": list(phrase),
        })
    return matched


def map_semantic_roles(
    parse_result: dict[str, Any],
    sense: dict[str, Any],
    *,
    voice: str | None = None,
) -> dict[str, Any]:
    """Map parser roles through the valency frames of one selected sense.

    The caller must explicitly supply voice="active" to enable mapping.
    Passive mapping is deliberately deferred until parser/morphology voice
    analysis can distinguish passive arguments from ordinary objects.
    """
    if not isinstance(parse_result, dict):
        raise TypeError("parse_result harus berupa dictionary hasil parser")
    if not isinstance(sense, dict):
        raise TypeError("sense harus berupa dictionary")
    if voice not in {None, "active", "passive"}:
        raise ValueError("voice harus None, 'active', atau 'passive'")

    sense_id = sense.get("sense_id")
    frames = sense.get("valency_frames")
    if not isinstance(frames, list) or not frames:
        return _unresolved("no_valency_frames", "Sense belum memiliki anotasi valensi.")

    if voice is None:
        result = _unresolved(
            "voice_not_confirmed",
            "Voice belum dikonfirmasi oleh lapisan morfologi/konteks; pemetaan ditahan.",
        )
        result["sense_id"] = sense_id
        return result
    if voice == "passive":
        result = _unresolved(
            "passive_mapping_not_implemented",
            "Pemetaan voice pasif belum diterapkan; fungsi sintaksis permukaan tidak boleh langsung disamakan dengan peran semantis.",
        )
        result["sense_id"] = sense_id
        return result

    if parse_result.get("status") != "parsed":
        result = _unresolved(
            "parser_not_fully_resolved",
            "Parser belum menghasilkan analisis parsed penuh; pemetaan semantis ditahan.",
        )
        result["sense_id"] = sense_id
        return result

    roles = parse_result.get("roles")
    if not isinstance(roles, dict):
        result = _unresolved("missing_parser_roles", "Hasil parser tidak memiliki objek roles.")
        result["sense_id"] = sense_id
        return result

    candidates: list[dict[str, Any]] = []
    for frame in frames:
        if not isinstance(frame, dict) or not isinstance(frame.get("arguments"), list):
            continue
        mapped_arguments = []
        compatible = True

        for argument in frame["arguments"]:
            if not isinstance(argument, dict):
                compatible = False
                break
            syntactic_role = argument.get("syntactic_role")
            role_field = _ROLE_FIELDS.get(syntactic_role)
            if role_field is None:
                compatible = False
                break

            required = argument.get("required")
            if not isinstance(required, bool):
                compatible = False
                break

            if syntactic_role == "OBL":
                raw_adjuncts = roles.get("adjuncts", [])
                if not isinstance(raw_adjuncts, list):
                    compatible = False
                    break
                realizations = argument.get("realizations", [])
                # Parser saat ini belum membedakan PP argumen inti dari PP
                # keterangan. Tanpa batas preposisi eksplisit, jangan menebak.
                has_explicit_constraint = any(
                    realization.get("type") == "PP"
                    and isinstance(realization.get("prepositions"), list)
                    and bool(realization.get("prepositions"))
                    for realization in realizations
                    if isinstance(realization, dict)
                )
                if not has_explicit_constraint:
                    compatible = False
                    break
                values = _oblique_values(raw_adjuncts, realizations)
            else:
                raw_values = roles.get(role_field, [])
                if not isinstance(raw_values, list) or not all(
                    isinstance(value, str) for value in raw_values
                ):
                    compatible = False
                    break
                values = list(raw_values)

            if not values and required:
                compatible = False
                break

            mapped_arguments.append({
                "argument_id": argument.get("argument_id"),
                "syntactic_role": syntactic_role,
                "semantic_role": argument.get("semantic_role"),
                "presence": "present" if values else "omitted",
                "value": values,
            })

        # Jangan menerima frame yang mengabaikan argumen inti yang sudah
        # dikenali parser. Tanpa pemeriksaan ini, frame intransitif dapat
        # keliru cocok pada kalimat yang juga memiliki objek/pelengkap.
        if compatible:
            for syntactic_role, field in (
                ("SUBJ", "subject"),
                ("OBJ", "object"),
                ("COMP", "complement"),
            ):
                surface_values = roles.get(field, [])
                if not isinstance(surface_values, list):
                    compatible = False
                    break
                if surface_values and not any(
                    isinstance(argument, dict)
                    and argument.get("syntactic_role") == syntactic_role
                    for argument in frame["arguments"]
                ):
                    compatible = False
                    break

        if compatible:
            candidates.append({
                "frame_id": frame.get("frame_id"),
                "arguments": mapped_arguments,
            })

    if not candidates:
        return {
            "status": "incompatible",
            "reason": "no_frame_matches_surface_roles",
            "sense_id": sense_id,
            "candidates": [],
            "notes": [
                "Tidak ada frame valensi yang cocok dengan argumen yang dikenali parser; tidak ada peran semantis yang dipaksakan."
            ],
        }

    return {
        "status": "mapped" if len(candidates) == 1 else "ambiguous",
        "reason": None if len(candidates) == 1 else "multiple_frames_match",
        "sense_id": sense_id,
        "candidates": candidates,
        "notes": (
            ["Satu frame cocok; pemetaan tetap bergantung pada ketepatan sense dan voice yang dipasok."]
            if len(candidates) == 1
            else ["Beberapa frame cocok; seluruh kandidat dipertahankan tanpa memilih semantic role secara otomatis."]
        ),
    }

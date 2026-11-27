"""Pemetaan konservatif fungsi sintaksis ke semantic role berbasis valensi.

Modul ini terpisah dari parser. Voice harus dikonfirmasi oleh lapisan analisis
morfologi/konteks. Pemetaan pasif sederhana membalik realisasi permukaan SUBJ/OBJ
ke argumen valensi: subjek permukaan menjadi OBJ (umumnya PATIENT), sedangkan
agen dapat muncul sebagai objek pascaverbal atau frasa PP berpreposisi "oleh".
Kasus yang tidak cocok dengan pola terbatas ini tetap unresolved.
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


def _map_passive_roles(
    parse_result: dict[str, Any],
    sense: dict[str, Any],
    frames: list[Any],
) -> dict[str, Any]:
    """Map one conservative di- passive surface pattern through active valency."""
    sense_id = sense.get("sense_id")
    roles = parse_result.get("roles")
    if not isinstance(roles, dict):
        result = _unresolved("missing_parser_roles", "Hasil parser tidak memiliki objek roles.")
        result["sense_id"] = sense_id
        return result

    surface_subject = roles.get("subject", [])
    surface_object = roles.get("object", [])
    adjuncts = roles.get("adjuncts", [])
    if not all(isinstance(values, list) and all(isinstance(v, str) for v in values)
               for values in (surface_subject, surface_object)):
        result = _unresolved("invalid_parser_roles", "Peran permukaan parser tidak valid.")
        result["sense_id"] = sense_id
        return result
    if not isinstance(adjuncts, list):
        result = _unresolved("invalid_parser_roles", "Daftar adjunct parser tidak valid.")
        result["sense_id"] = sense_id
        return result
    if not surface_subject:
        result = _unresolved("passive_patient_not_identified", "Subjek permukaan/pasien pasif belum dikenali.")
        result["sense_id"] = sense_id
        return result

    oleh_phrases = []
    for adjunct in adjuncts:
        if not isinstance(adjunct, dict):
            continue
        if isinstance(adjunct.get("preposition"), str) and adjunct["preposition"].casefold() == "oleh":
            phrase = adjunct.get("phrase")
            if isinstance(phrase, list) and phrase and all(isinstance(v, str) for v in phrase):
                oleh_phrases.append(phrase)
    if oleh_phrases and surface_object:
        result = _unresolved(
            "passive_agent_realization_conflict",
            "Agen muncul sekaligus sebagai objek pascaverbal dan frasa oleh; pemetaan ditahan.",
        )
        result["sense_id"] = sense_id
        return result
    if len(oleh_phrases) > 1:
        result = _unresolved("multiple_passive_agent_phrases", "Lebih dari satu frasa oleh ditemukan.")
        result["sense_id"] = sense_id
        return result
    if surface_object and len(surface_object) != 1:
        result = _unresolved("multiple_postverbal_passive_agents", "Rentang objek pascaverbal belum dapat dipastikan sebagai satu agen.")
        result["sense_id"] = sense_id
        return result

    agent_values = surface_object or (oleh_phrases[0] if oleh_phrases else [])
    agent_source = "postverbal_agent" if surface_object else (
        "oleh_phrase" if oleh_phrases else "omitted"
    )
    candidates: list[dict[str, Any]] = []
    for frame in frames:
        if not isinstance(frame, dict) or not isinstance(frame.get("arguments"), list):
            continue
        subj_args = [
            a for a in frame["arguments"]
            if isinstance(a, dict) and a.get("syntactic_role") == "SUBJ"
        ]
        obj_args = [
            a for a in frame["arguments"]
            if isinstance(a, dict) and a.get("syntactic_role") == "OBJ"
        ]
        # Passive remapping is limited to frames with one SUBJ and one OBJ.
        if len(subj_args) != 1 or len(obj_args) != 1:
            continue
        subject_arg, object_arg = subj_args[0], obj_args[0]
        if not isinstance(subject_arg.get("realizations"), list) or not isinstance(object_arg.get("realizations"), list):
            continue
        if not agent_values and subject_arg.get("required") is not True:
            # Requiredness is active-frame valency. Passive agent omission is
            # licensed independently by the passive construction.
            pass
        if agent_values and subject_arg.get("required") is not True:
            continue
        if object_arg.get("required") is not True:
            # This pilot only handles a clearly realized passive patient.
            continue
        mapped = [
            {
                "argument_id": subject_arg.get("argument_id"),
                "syntactic_role": "SUBJ",
                "surface_role": "OBJ" if agent_source == "postverbal_agent" else (
                    "OBL" if agent_source == "oleh_phrase" else None
                ),
                "semantic_role": subject_arg.get("semantic_role"),
                "presence": "present" if agent_values else "omitted",
                "value": list(agent_values),
                "realization": agent_source,
            },
            {
                "argument_id": object_arg.get("argument_id"),
                "syntactic_role": "OBJ",
                "surface_role": "SUBJ",
                "semantic_role": object_arg.get("semantic_role"),
                "presence": "present",
                "value": list(surface_subject),
                "realization": "passive_surface_subject",
            },
        ]
        candidates.append({"frame_id": frame.get("frame_id"), "arguments": mapped})

    if not candidates:
        result = _unresolved(
            "no_supported_passive_frame",
            "Pola pasif ini memerlukan satu argumen SUBJ dan satu OBJ dalam frame valensi; tidak ada frame yang dapat dipetakan dengan aman.",
        )
        result["sense_id"] = sense_id
        return result

    return {
        "status": "mapped" if len(candidates) == 1 else "ambiguous",
        "reason": None if len(candidates) == 1 else "multiple_frames_match",
        "sense_id": sense_id,
        "candidates": candidates,
        "notes": [
            "Pemetaan pasif terbatas: subjek permukaan dipetakan ke argumen OBJ valensi; agen opsional dipetakan ke argumen SUBJ.",
            "Bentuk pasif tanpa agen mengizinkan argumen SUBJ valensi tidak terealisasi, meskipun required pada frame aktif.",
            "Hanya pola klausa sederhana dengan voice pasif yang telah dikonfirmasi yang didukung; ini bukan pemetaan pasif umum untuk semua konstruksi.",
        ],
    }


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

    if voice == "passive":
        if parse_result.get("parser_method") != "conservative_svo_v4":
            result = _unresolved(
                "unsupported_passive_parse_method",
                "Pemetaan pasif hanya menerima hasil klausa sederhana conservative_svo_v4.",
            )
            result["sense_id"] = sense_id
            return result
        structure = parse_result.get("predicate_structure")
        if not isinstance(structure, dict) or not isinstance(structure.get("head"), str):
            result = _unresolved(
                "passive_predicate_head_unavailable",
                "Kepala predikat tidak tersedia untuk mengikat bukti voice pasif.",
            )
            result["sense_id"] = sense_id
            return result
        return _map_passive_roles(parse_result, sense, frames)

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

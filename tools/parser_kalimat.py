"""Parser prototipe konservatif untuk pola klausa sederhana Bahasa Indonesia.

Versi ini mengenali kerangka S-P, S-P-O, keterangan berpreposisi, dan
rentang frasa nominal sederhana tanpa memaksakan analisis internal frasa.
Parser tidak menebak fungsi kata yang POS-nya ambigu/tidak diketahui dan tidak
mengklaim analisis lengkap untuk kalimat majemuk atau konstruksi kompleks.
"""
from __future__ import annotations

from typing import Any


_TERMINAL_PUNCTUATION = {".", "!", "?", "…"}
_NOMINAL_POS = {"NOUN", "PRON"}
_OBJECT_PHRASE_POS = {"NOUN", "PRON", "NUM", "ADJ"}
_NOMINAL_PHRASE_POS = {"NOUN", "PRON", "NUM", "ADJ"}
_ADVERBIAL_PREDICATE_POS = {"ADV"}
_NEGATION_MARKERS = {"tidak", "belum"}


def _effective_pos(item: dict[str, Any]) -> str | None:
    """Use contextual POS only when explicitly selected; otherwise a singleton."""
    context_pos = item.get("context_pos")
    context_status = item.get("pos_context_status")
    if context_pos and context_status in {"selected_by_context", "unambiguous"}:
        return context_pos

    labels = item.get("pos", [])
    if not isinstance(labels, list):
        raise ValueError("field pos setiap token harus berupa array")
    if item.get("pos_status") == "identified" and len(labels) == 1:
        return labels[0]
    if len(labels) == 1 and context_status is None:
        return labels[0]
    return None


def _phrase_span(words: list[dict[str, Any]], head: int, lower: int, upper: int) -> list[int]:
    """Collect one contiguous nominal phrase around a known nominal head."""
    start = head
    end = head + 1
    while start > lower and words[start - 1]["pos"] in _NOMINAL_PHRASE_POS:
        start -= 1
    while end < upper and words[end]["pos"] in _NOMINAL_PHRASE_POS:
        end += 1
    return list(range(start, end))


def parse_sentence(analysis: dict[str, Any]) -> dict[str, Any]:
    """Return a cautious role skeleton from POS-tagged/contextualized tokens.

    Input is the output of tag_pos(), preferably followed by
    disambiguate_pos_context(). Terminal punctuation is ignored. Internal
    punctuation and unresolved POS are reported rather than guessed.
    """
    if not isinstance(analysis, dict):
        raise TypeError("analysis harus berupa dictionary hasil analisis POS")
    tokens = analysis.get("tokens")
    if not isinstance(tokens, list):
        raise ValueError("analysis harus memiliki array tokens")

    words: list[dict[str, Any]] = []
    for index, item in enumerate(tokens):
        if not isinstance(item, dict):
            raise ValueError("setiap token harus berupa objek")
        token = item.get("token")
        if not isinstance(token, str):
            raise ValueError("setiap token harus memiliki field token berupa teks")
        if item.get("kind") == "punctuation" or item.get("pos_status") == "not_applicable":
            if token in _TERMINAL_PUNCTUATION:
                continue
            return {
                "parser_method": "conservative_svo_v2",
                "status": "unsupported",
                "pattern": None,
                "roles": {
                    "subject": [], "predicate": [], "object": [],
                    "adjuncts": [], "complement": [],
                },
                "unresolved_tokens": [],
                "notes": [f"Tanda baca internal {token!r} belum diparse sebagai pemisah klausa."],
            }
        words.append({
            "index": index,
            "token": token,
            "pos": _effective_pos(item),
            "source": item,
        })

    verb_positions = [i for i, item in enumerate(words) if item["pos"] == "VERB"]
    if not verb_positions:
        return {
            "parser_method": "conservative_svo_v2",
            "status": "unresolved",
            "pattern": None,
            "roles": {
                "subject": [], "predicate": [], "object": [],
                "adjuncts": [], "complement": [],
            },
            "unresolved_tokens": [item["token"] for item in words],
            "notes": ["Predikat VERB yang pasti belum ditemukan."],
        }

    verb_pos = verb_positions[0]
    subject_heads = [
        i for i in range(verb_pos) if words[i]["pos"] in _NOMINAL_POS
    ]
    if not subject_heads:
        return {
            "parser_method": "conservative_svo_v2",
            "status": "unresolved",
            "pattern": None,
            "roles": {
                "subject": [], "predicate": [words[verb_pos]["token"]],
                "object": [], "adjuncts": [], "complement": [],
            },
            "unresolved_tokens": [item["token"] for item in words if item["pos"] is None],
            "notes": ["Subjek eksplisit sebelum predikat belum ditemukan; inversi dan subjek tersirat belum ditangani."],
        }

    # Ambil frasa nominal yang paling dekat dengan predikat. Kata sifat/angka
    # yang berdampingan ikut menjadi bagian frasa, tetapi tidak ditafsirkan
    # lebih jauh sebagai inti atau pewatas.
    subject_positions = _phrase_span(words, subject_heads[-1], 0, verb_pos)
    subject_set = set(subject_positions)
    predicate_positions = [verb_pos]
    cursor = verb_pos - 1
    while cursor >= 0 and (
        words[cursor]["pos"] in _ADVERBIAL_PREDICATE_POS
        or (
            words[cursor]["token"].casefold() in _NEGATION_MARKERS
            and words[cursor]["pos"] in {"ADV", "PART"}
        )
    ):
        predicate_positions.insert(0, cursor)
        cursor -= 1

    object_positions: list[int] = []
    adjuncts: list[dict[str, Any]] = []
    assigned = subject_set | set(predicate_positions)
    cursor = verb_pos + 1

    # Cari kepala nominal pertama sebelum batas klausa/frasa preposisional,
    # lalu ambil rentang frasa nominal sederhana di sekitarnya.
    object_head = None
    while cursor < len(words) and words[cursor]["pos"] not in {"PREP", "CONJ", "VERB"}:
        if words[cursor]["pos"] in _NOMINAL_POS:
            object_head = cursor
            break
        cursor += 1
    if object_head is not None:
        object_positions = _phrase_span(words, object_head, verb_pos + 1, len(words))
        assigned.update(object_positions)

    # Keterangan berpreposisi sederhana: preposisi + frasa nominal sesudahnya.
    while cursor < len(words):
        if words[cursor]["pos"] == "PREP":
            marker = cursor
            phrase_positions: list[int] = []
            cursor += 1
            while cursor < len(words) and words[cursor]["pos"] in _OBJECT_PHRASE_POS:
                phrase_positions.append(cursor)
                cursor += 1
            if phrase_positions:
                adjuncts.append({
                    "preposition": words[marker]["token"],
                    "phrase": [words[i]["token"] for i in phrase_positions],
                })
                assigned.add(marker)
                assigned.update(phrase_positions)
            continue
        cursor += 1

    roles = {
        "subject": [words[i]["token"] for i in subject_positions],
        "predicate": [words[i]["token"] for i in predicate_positions],
        "object": [words[i]["token"] for i in object_positions],
        "adjuncts": adjuncts,
        "complement": [],
    }
    unresolved = [
        item["token"] for i, item in enumerate(words)
        if i not in assigned
    ]

    pattern_parts = ["S", "P"]
    if object_positions:
        pattern_parts.append("O")
    if adjuncts:
        pattern_parts.append("K")
    return {
        "parser_method": "conservative_svo_v2",
        "status": "partial" if unresolved else "parsed",
        "pattern": "-".join(pattern_parts),
        "roles": roles,
        "unresolved_tokens": unresolved,
        "notes": [
            "Kerangka klausa sederhana; bukan analisis sintaksis lengkap.",
            "Frasa nominal dilaporkan sebagai rentang datar; inti dan pewatasnya belum dianalisis. Negasi verbal 'tidak' dan 'belum' dikenali secara terbatas; negasi predikat adjektival/nominal, pelengkap, koordinasi, klausa majemuk, dan subjek tersirat belum dimodelkan.",
        ],
    }

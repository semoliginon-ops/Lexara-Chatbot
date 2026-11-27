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
_MODAL_VERBS = {"mau", "ingin", "hendak"}
_LINKING_PREDICATES = {"menjadi", "tampak"}


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
                "parser_method": "conservative_svo_v4",
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
        # Predikat nonverbal sederhana dengan penanda subjek yang cukup jelas.
        nominal_heads = [i for i, item in enumerate(words) if item["pos"] in _NOMINAL_POS]
        adjective_heads = [i for i, item in enumerate(words) if item["pos"] == "ADJ" and i > 0]
        predicate_start = None
        if adjective_heads:
            candidate = adjective_heads[0]
            subject_prefix = words[:candidate]
            anchored = bool(subject_prefix) and (
                subject_prefix[0]["pos"] == "PRON"
                or any(item["token"].casefold() in {"ini", "itu"} for item in subject_prefix)
            )
            if anchored and all(item["pos"] in _NOMINAL_PHRASE_POS | {"NUM"} for item in subject_prefix):
                predicate_start = candidate
        if predicate_start is None and len(nominal_heads) >= 2:
            second_head = nominal_heads[1]
            candidate_start = second_head - 1 if second_head > 0 and words[second_head - 1]["pos"] == "NUM" else second_head
            predicate_tokens = words[candidate_start:]
            if (
                nominal_heads[0] == 0
                and len(predicate_tokens) >= 2
                and words[candidate_start]["pos"] == "NUM"
            ):
                predicate_start = candidate_start
        if predicate_start is not None:
            return {
                "parser_method": "conservative_nonverbal_v1",
                "status": "parsed",
                "pattern": "S-P",
                "roles": {
                    "subject": [item["token"] for item in words[:predicate_start]],
                    "predicate": [item["token"] for item in words[predicate_start:]],
                    "object": [], "adjuncts": [], "complement": [],
                },
                "unresolved_tokens": [],
                "notes": [
                    "Predikat nonverbal sederhana dikenali secara heuristik.",
                    "Frasa adjektival dan nominal belum dianalisis secara internal; konstruksi tanpa penanda subjek yang cukup tetap unresolved.",
                ],
            }
        return {
            "parser_method": "conservative_svo_v4",
            "status": "unresolved",
            "pattern": None,
            "roles": {
                "subject": [], "predicate": [], "object": [],
                "adjuncts": [], "complement": [],
            },
            "unresolved_tokens": [item["token"] for item in words],
            "notes": ["Predikat VERB atau pola predikat nonverbal sederhana yang cukup pasti belum ditemukan."],
        }

    # Kata kehendak yang berlabel VERB dapat menjadi verba bantu ketika
    # diikuti verba leksikal. Jika berdiri sendiri, tetap menjadi predikat.
    lexical_positions = [
        i for i in verb_positions
        if words[i]["token"].casefold() not in _MODAL_VERBS
    ]
    verb_pos = lexical_positions[0] if lexical_positions else verb_positions[0]
    subject_heads = [
        i for i in range(verb_pos) if words[i]["pos"] in _NOMINAL_POS
    ]
    if not subject_heads:
        return {
            "parser_method": "conservative_svo_v4",
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
    subject_head = subject_heads[-1]
    subject_lower = 0
    for prior in range(subject_head - 1, -1, -1):
        if words[prior]["pos"] == "PREP":
            subject_lower = prior + 1
            break
    subject_positions = _phrase_span(words, subject_head, subject_lower, verb_pos)
    subject_set = set(subject_positions)
    predicate_positions = [verb_pos]
    cursor = verb_pos - 1
    while cursor >= 0 and (
        words[cursor]["pos"] in _ADVERBIAL_PREDICATE_POS
        or (
            words[cursor]["token"].casefold() in _MODAL_VERBS
            and words[cursor]["pos"] == "VERB"
        )
        or (
            words[cursor]["token"].casefold() in _NEGATION_MARKERS
            and words[cursor]["pos"] in {"ADV", "PART"}
        )
    ):
        predicate_positions.insert(0, cursor)
        cursor -= 1

    object_positions: list[int] = []
    complement_positions: list[int] = []
    adjuncts: list[dict[str, Any]] = []
    assigned = subject_set | set(predicate_positions)

    # Keterangan berpreposisi di awal kalimat dapat mendahului subjek.
    # Hanya rentang PREP + frasa nominal yang selesai tepat sebelum subjek
    # yang diterima; pola lain tetap dibiarkan unresolved.
    subject_start = min(subject_positions) if subject_positions else verb_pos
    prefix_cursor = 0
    while prefix_cursor < subject_start:
        if words[prefix_cursor]["pos"] != "PREP":
            prefix_cursor += 1
            continue
        phrase_positions: list[int] = []
        scan = prefix_cursor + 1
        while scan < subject_start and words[scan]["pos"] in _OBJECT_PHRASE_POS:
            phrase_positions.append(scan)
            scan += 1
        if phrase_positions and scan == subject_start:
            adjuncts.append({
                "preposition": words[prefix_cursor]["token"],
                "phrase": [words[i]["token"] for i in phrase_positions],
            })
            assigned.add(prefix_cursor)
            assigned.update(phrase_positions)
            prefix_cursor = scan
        else:
            prefix_cursor += 1

    cursor = verb_pos + 1

    # Verba penghubung tertentu memperkenalkan pelengkap, bukan objek.
    # Aturan dibatasi pada verba eksplisit dan pelengkap nominal/adjektival.
    if words[verb_pos]["token"].casefold() in _LINKING_PREDICATES:
        candidate = cursor
        if candidate < len(words) and words[candidate]["pos"] == "NUM":
            noun_head = next(
                (i for i in range(candidate + 1, len(words)) if words[i]["pos"] == "NOUN"),
                None,
            )
            if noun_head is not None:
                complement_positions = list(range(candidate, noun_head + 1))
        elif candidate < len(words) and words[candidate]["pos"] == "NOUN":
            complement_positions = _phrase_span(words, candidate, candidate, len(words))
        elif candidate < len(words) and words[candidate]["pos"] == "ADJ":
            end = candidate + 1
            while end < len(words) and words[end]["pos"] == "ADJ":
                end += 1
            complement_positions = list(range(candidate, end))
        if complement_positions:
            assigned.update(complement_positions)
            cursor = complement_positions[-1] + 1

    # Cari kepala nominal pertama sebelum batas klausa/frasa preposisional,
    # lalu ambil rentang frasa nominal sederhana di sekitarnya.
    object_head = None
    while cursor < len(words) and words[cursor]["pos"] not in {"PREP", "CONJ", "VERB"}:
        if words[cursor]["pos"] in _NOMINAL_POS:
            object_head = cursor
            break
        cursor += 1
    if object_head is not None:
        object_positions = _phrase_span(words, object_head, cursor, len(words))
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
        "complement": [words[i]["token"] for i in complement_positions],
    }
    unresolved = [
        item["token"] for i, item in enumerate(words)
        if i not in assigned
    ]

    pattern_parts = ["S", "P"]
    if object_positions:
        pattern_parts.append("O")
    if complement_positions:
        pattern_parts.append("Pel")
    if adjuncts:
        pattern_parts.append("K")
    return {
        "parser_method": "conservative_svo_v4",
        "status": "partial" if unresolved else "parsed",
        "pattern": "-".join(pattern_parts),
        "roles": roles,
        "unresolved_tokens": unresolved,
        "notes": [
            "Kerangka klausa sederhana; bukan analisis sintaksis lengkap.",
            "Frasa nominal dilaporkan sebagai rentang datar; inti dan pewatasnya belum dianalisis. Negasi verbal 'tidak' dan 'belum' dikenali secara terbatas. Verba kehendak 'mau', 'ingin', dan 'hendak' digabung ke rentang predikat hanya jika diikuti verba leksikal; penggunaan tunggal tetap dipertahankan sebagai predikat. Predikat nonverbal adjektival/nominal sederhana dikenali secara heuristik; modalitas lain, pelengkap, koordinasi, klausa majemuk, dan subjek tersirat belum dimodelkan.",
        ],
    }

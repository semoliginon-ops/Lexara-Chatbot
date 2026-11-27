"""Parser prototipe konservatif v1.8 untuk pola klausa sederhana Bahasa Indonesia.

Versi ini mengenali kerangka S-P, S-P-O, keterangan berpreposisi, dan
rentang frasa nominal sederhana tanpa memaksakan analisis internal frasa.
Parser tidak menebak fungsi kata yang POS-nya ambigu/tidak diketahui dan tidak
mengklaim analisis lengkap untuk kalimat majemuk atau konstruksi kompleks.
Versi 1.6 menambahkan rincian kepala predikat verbal; v1.7 memperluas modalitas;
v1.8 mengenali empat keterangan waktu ADV yang eksplisit di awal klausa.
"""
from __future__ import annotations

from typing import Any


_TERMINAL_PUNCTUATION = {".", "!", "?", "…"}
_NOMINAL_POS = {"NOUN", "PRON"}
_OBJECT_PHRASE_POS = {"NOUN", "PRON", "NUM", "ADJ"}
_NOMINAL_PHRASE_POS = {"NOUN", "PRON", "NUM", "ADJ"}
_ADVERBIAL_PREDICATE_POS = {"ADV"}
_NEGATION_MARKERS = {"tidak", "belum"}
_MODAL_VERBS = {"mau", "ingin", "hendak", "bisa"}
_MODAL_ADVERBS = {"akan"}
_FRONTED_TEMPORAL_ADVERBS = {"besok", "nanti", "sekarang", "tadi"}
_LINKING_PREDICATES = {"menjadi", "tampak"}

# Klasifikasi eksplisit fungsi penghubung; tidak menyimpulkan relasi untuk kata lain.
_CONNECTOR_RELATIONS = {
    "dan": "penambahan",
    "atau": "alternatif",
    "tetapi": "pertentangan",
    "namun": "pertentangan",
    "karena": "sebab",
    "sebab": "sebab",
    "walaupun": "konsesi",
    "meskipun": "konsesi",
    "lalu": "urutan",
    "kemudian": "urutan",
    "ketika": "temporal",
}


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


def _predicate_structure(
    words: list[dict[str, Any]], positions: list[int], head_position: int
) -> dict[str, Any]:
    """Expose the lexical predicate head separately from its recognized modifiers."""
    modifiers = []
    for position in positions:
        if position == head_position:
            continue
        item = words[position]
        token = item["token"].casefold()
        if token in _NEGATION_MARKERS:
            kind = "negation"
        elif (
            (token in _MODAL_VERBS and item["pos"] == "VERB")
            or (token in _MODAL_ADVERBS and item["pos"] == "ADV")
        ):
            kind = "modal"
        else:
            kind = "adverbial"
        modifiers.append({"token": item["token"], "kind": kind})
    return {
        "head": words[head_position]["token"],
        "modifiers": modifiers,
    }


def _coordinated_phrase_span(
    words: list[dict[str, Any]], positions: list[int], lower: int, upper: int
) -> list[int]:
    """Expand a nominal phrase across explicit conjunctions only."""
    if not positions:
        return positions
    start, end = positions[0], positions[-1] + 1
    while start - 2 >= lower and words[start - 1]["pos"] == "CONJ":
        previous_head = start - 2
        if words[previous_head]["pos"] not in _NOMINAL_POS:
            break
        previous = _phrase_span(words, previous_head, lower, start - 1)
        start = previous[0]
    while end + 1 < upper and words[end]["pos"] == "CONJ":
        next_head = end + 1
        if words[next_head]["pos"] not in _NOMINAL_POS:
            break
        following = _phrase_span(words, next_head, end + 1, upper)
        end = following[-1] + 1
    return list(range(start, end))


def _elliptical_concessive_analysis(items: list[dict[str, Any]]) -> dict[str, Any] | None:
    """Recognize only an explicit adverb + adjectival predicate without a subject."""
    words: list[dict[str, str]] = []
    for item in items:
        if not isinstance(item, dict) or not isinstance(item.get("token"), str):
            return None
        pos = _effective_pos(item)
        if pos not in {"ADV", "ADJ"}:
            return None
        words.append({"token": item["token"], "pos": pos})
    if not words or words[-1]["pos"] != "ADJ":
        return None
    if not any(word["pos"] == "ADJ" for word in words):
        return None
    return {
        "parser_method": "conservative_elliptical_nonverbal_v1",
        "status": "partial",
        "pattern": "P-ELIPTIS",
        "roles": {
            "subject": [],
            "predicate": [word["token"] for word in words],
            "object": [],
            "adjuncts": [],
            "complement": [],
        },
        "unresolved_tokens": [],
        "notes": [
            "Predikat adjektival klausa konsesif dikenali tanpa subjek eksplisit.",
            "Subjek yang dilesapkan tidak disimpulkan atau disalin dari klausa utama; hasil tetap partial.",
        ],
    }


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

    # Klausa subordinatif di depan kalimat: penanda + klausa + koma + klausa utama.
    # Dibatasi pada penghubung sebab, temporal, dan konsesi yang dipetakan eksplisit.
    if tokens and isinstance(tokens[0], dict):
        marker = tokens[0].get("token")
        marker_key = marker.casefold() if isinstance(marker, str) else ""
        marker_relation = _CONNECTOR_RELATIONS.get(marker_key)
        comma_positions = [
            i for i, item in enumerate(tokens)
            if isinstance(item, dict) and item.get("token") == ","
        ]
        allowed_fronted_relations = {"sebab", "temporal", "konsesi"}
        if marker_relation in allowed_fronted_relations and len(comma_positions) == 1:
            comma = comma_positions[0]
            prefix_items = tokens[1:comma]
            main_items = tokens[comma + 1:]
            prefix_has_only_words = all(
                isinstance(item, dict)
                and item.get("token") not in {",", ".", "!", "?", "…", ":", ";"}
                for item in prefix_items
            )
            main_has_no_internal_punctuation = all(
                isinstance(item, dict)
                and (
                    item.get("token") not in {",", ":", ";"}
                    or item.get("token") in _TERMINAL_PUNCTUATION
                )
                for item in main_items
            )
            if prefix_items and main_items and prefix_has_only_words and main_has_no_internal_punctuation:
                subordinate = parse_sentence({"tokens": prefix_items})
                if subordinate["status"] == "unresolved" and marker_relation == "konsesi":
                    elliptical = _elliptical_concessive_analysis(prefix_items)
                    if elliptical is not None:
                        subordinate = elliptical
                main_clause = parse_sentence({"tokens": main_items})
                acceptable = {"parsed", "partial"}
                if subordinate["status"] in acceptable and main_clause["status"] in acceptable:
                    status = (
                        "parsed"
                        if subordinate["status"] == "parsed" and main_clause["status"] == "parsed"
                        else "partial"
                    )
                    return {
                        "parser_method": "conservative_fronted_subordination_v1",
                        "status": status,
                        "pattern": "KLAUSA-SUBORDINATIF",
                        "roles": {
                            "subject": [], "predicate": [], "object": [],
                            "adjuncts": [], "complement": [],
                        },
                        "clauses": [
                            {
                                "subordinator": marker,
                                "relation_to_next": marker_relation,
                                "analysis": subordinate,
                            },
                            {
                                "subordinator": None,
                                "relation_to_previous": marker_relation,
                                "analysis": main_clause,
                            },
                        ],
                        "unresolved_tokens": (
                            subordinate["unresolved_tokens"] + main_clause["unresolved_tokens"]
                        ),
                        "notes": [
                            "Klausa subordinatif awal dikenali melalui penghubung eksplisit dan koma pemisah.",
                            "Klausa utama dianalisis terpisah; relasi dicatat sebagai metadata penghubung, bukan pemahaman semantik lengkap.",
                            "Klausa awal biasanya memerlukan predikat teridentifikasi; klausa konsesif eliptis dengan predikat adjektival eksplisit diterima secara partial tanpa menebak subjek.",
                        ],
                    }

    # Klausa subordinatif setelah klausa utama. Periksa sebelum koordinasi
    # agar "karena/ketika/walaupun" tidak salah dibaca sebagai konjungsi setara.
    conjunction_positions = [
        i for i, item in enumerate(tokens)
        if isinstance(item, dict) and _effective_pos(item) == "CONJ"
    ]
    subordinating_positions = [
        i for i in conjunction_positions
        if _CONNECTOR_RELATIONS.get(
            str(tokens[i].get("token", "")).casefold()
        ) in {"sebab", "temporal", "konsesi"}
    ]
    if len(subordinating_positions) == 1:
        marker_position = subordinating_positions[0]
        if marker_position > 0 and marker_position < len(tokens) - 1:
            main_items = tokens[:marker_position]
            subordinate_items = tokens[marker_position + 1:]
            main_clause = parse_sentence({"tokens": main_items})
            subordinate = parse_sentence({"tokens": subordinate_items})
            acceptable = {"parsed", "partial"}
            if main_clause["status"] in acceptable and subordinate["status"] in acceptable:
                relation = _CONNECTOR_RELATIONS[
                    str(tokens[marker_position].get("token", "")).casefold()
                ]
                status = (
                    "parsed"
                    if main_clause["status"] == "parsed" and subordinate["status"] == "parsed"
                    else "partial"
                )
                return {
                    "parser_method": "conservative_postposed_subordination_v1",
                    "status": status,
                    "pattern": "KLAUSA-SUBORDINATIF",
                    "roles": {
                        "subject": [], "predicate": [], "object": [],
                        "adjuncts": [], "complement": [],
                    },
                    "clauses": [
                        {
                            "subordinator": None,
                            "relation_to_next": relation,
                            "analysis": main_clause,
                        },
                        {
                            "subordinator": tokens[marker_position]["token"],
                            "relation_to_previous": relation,
                            "analysis": subordinate,
                        },
                    ],
                    "unresolved_tokens": (
                        main_clause["unresolved_tokens"] + subordinate["unresolved_tokens"]
                    ),
                    "notes": [
                        "Klausa utama mendahului klausa subordinatif yang ditandai penghubung eksplisit.",
                        "Relasi dicatat sebagai metadata penghubung; parser tidak mengklaim pemahaman semantik lengkap.",
                    ],
                }

    # Koordinasi klausa: pisahkan beberapa segmen hanya jika setiap segmen
    # memiliki verba teridentifikasi. Koordinasi frasa nominal tetap ditangani
    # parser satu klausa karena segmen nominalnya tidak lolos syarat ini.
    conjunctions = [
        i for i, item in enumerate(tokens)
        if isinstance(item, dict) and _effective_pos(item) == "CONJ"
    ]
    if conjunctions:
        boundaries = [-1, *conjunctions, len(tokens)]
        segments = [
            tokens[boundaries[i] + 1:boundaries[i + 1]]
            for i in range(len(boundaries) - 1)
        ]
        segments_have_verbs = all(
            segment
            and any(
                isinstance(item, dict) and _effective_pos(item) == "VERB"
                for item in segment
            )
            for segment in segments
        )
        if segments_have_verbs:
            clause_results = [
                parse_sentence({"tokens": segment})
                for segment in segments
            ]
            acceptable = {"parsed", "partial"}
            if all(result["status"] in acceptable for result in clause_results):
                status = (
                    "parsed"
                    if all(result["status"] == "parsed" for result in clause_results)
                    else "partial"
                )
                clauses = []
                for index, result in enumerate(clause_results):
                    connector = (
                        None if index == 0
                        else tokens[conjunctions[index - 1]]["token"]
                    )
                    clauses.append({
                        "connector": connector,
                        "relation_to_previous": (
                            None if connector is None
                            else _CONNECTOR_RELATIONS.get(
                                connector.casefold(), "belum_diklasifikasikan"
                            )
                        ),
                        "analysis": result,
                    })
                return {
                    "parser_method": "conservative_coordination_v2",
                    "status": status,
                    "pattern": "KLAUSA-KOORDINATIF",
                    "roles": {
                        "subject": [], "predicate": [], "object": [],
                        "adjuncts": [], "complement": [],
                    },
                    "clauses": clauses,
                    "unresolved_tokens": [
                        token
                        for result in clause_results
                        for token in result["unresolved_tokens"]
                    ],
                    "notes": [
                        "Setiap segmen klausa dianalisis terpisah setelah dipisahkan oleh konjungsi eksplisit.",
                        "Semua segmen harus memiliki verba teridentifikasi; koordinasi frasa nominal tetap diproses sebagai satu klausa.",
                        "Relasi penghubung hanya diberi label untuk daftar konjungsi eksplisit; arah sebab-akibat, cakupan klausa, dan relasi semantik yang lebih rinci belum dianalisis.",
                    ],
                }

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
    # Nomina di dalam frasa berpreposisi bukan kandidat subjek.
    # Tandai seluruh rentang PREP + frasa nominal sebelum predikat agar
    # "di rumah" tidak keliru dipilih sebagai subjek pada "Di rumah terdengar suara".
    prepositional_positions: set[int] = set()
    scan = 0
    while scan < verb_pos:
        if words[scan]["pos"] != "PREP":
            scan += 1
            continue
        prepositional_positions.add(scan)
        scan += 1
        while scan < verb_pos and words[scan]["pos"] in _OBJECT_PHRASE_POS:
            prepositional_positions.add(scan)
            scan += 1

    subject_heads = [
        i for i in range(verb_pos)
        if words[i]["pos"] in _NOMINAL_POS and i not in prepositional_positions
    ]
    if not subject_heads:
        # Catat keterangan berpreposisi/temporal di awal, tetapi jangan
        # mengangkat nomina setelah verba menjadi subjek atau objek secara otomatis.
        leading_adjuncts: list[dict[str, Any]] = []
        leading_positions: set[int] = set()
        prefix_cursor = 0
        while prefix_cursor < verb_pos:
            current = words[prefix_cursor]
            if (
                current["pos"] == "ADV"
                and current["token"].casefold() in _FRONTED_TEMPORAL_ADVERBS
            ):
                leading_adjuncts.append({
                    "adverb": current["token"],
                    "kind": "temporal",
                })
                leading_positions.add(prefix_cursor)
                prefix_cursor += 1
                continue
            if current["pos"] != "PREP":
                break
            marker_position = prefix_cursor
            scan = marker_position + 1
            phrase_positions: list[int] = []
            while scan < verb_pos and words[scan]["pos"] in _OBJECT_PHRASE_POS:
                phrase_positions.append(scan)
                scan += 1
            if not phrase_positions:
                break
            leading_adjuncts.append({
                "preposition": words[marker_position]["token"],
                "phrase": [words[i]["token"] for i in phrase_positions],
            })
            leading_positions.add(marker_position)
            leading_positions.update(phrase_positions)
            prefix_cursor = scan

        assigned_without_subject = leading_positions | {verb_pos}
        unresolved_without_subject = [
            item["token"] for i, item in enumerate(words)
            if i not in assigned_without_subject
        ]
        return {
            "parser_method": "conservative_svo_v4",
            "status": "unresolved",
            "pattern": None,
            "roles": {
                "subject": [], "predicate": [words[verb_pos]["token"]],
                "object": [], "adjuncts": leading_adjuncts, "complement": [],
            },
            "unresolved_tokens": unresolved_without_subject,
            "notes": [
                "Subjek eksplisit sebelum predikat belum ditemukan; inversi dan subjek tersirat belum ditangani.",
                "Nomina di dalam frasa berpreposisi awal dicatat sebagai keterangan, bukan kandidat subjek; nomina setelah predikat tidak otomatis ditetapkan sebagai subjek atau objek.",
            ],
        }

    # Ambil frasa nominal yang paling dekat dengan predikat. Kata sifat/angka
    # yang berdampingan ikut menjadi bagian frasa, tetapi tidak ditafsirkan
    # lebih jauh sebagai inti atau pewatas.
    subject_head = subject_heads[-1]
    subject_lower = 0
    for prior in range(subject_head - 1, -1, -1):
        if words[prior]["pos"] == "PREP":
            subject_lower = subject_head
            break
    subject_positions = _phrase_span(words, subject_head, subject_lower, verb_pos)
    subject_positions = _coordinated_phrase_span(words, subject_positions, subject_lower, verb_pos)
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
            words[cursor]["token"].casefold() in _MODAL_ADVERBS
            and words[cursor]["pos"] == "ADV"
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

    # Keterangan berpreposisi dan empat ADV temporal eksplisit dapat
    # mendahului subjek. ADV lain tidak otomatis dianggap keterangan waktu.
    subject_start = min(subject_positions) if subject_positions else verb_pos
    prefix_cursor = 0
    fronted_adjuncts: list[dict[str, Any]] = []
    fronted_positions: set[int] = set()
    prefix_is_complete = True
    while prefix_cursor < subject_start:
        current = words[prefix_cursor]
        if (
            current["pos"] == "ADV"
            and current["token"].casefold() in _FRONTED_TEMPORAL_ADVERBS
        ):
            fronted_adjuncts.append({
                "adverb": current["token"],
                "kind": "temporal",
            })
            fronted_positions.add(prefix_cursor)
            prefix_cursor += 1
            continue
        if current["pos"] != "PREP":
            prefix_is_complete = False
            break
        marker = prefix_cursor
        scan = marker + 1
        phrase_positions: list[int] = []
        while scan < subject_start and words[scan]["pos"] in _OBJECT_PHRASE_POS:
            phrase_positions.append(scan)
            scan += 1
        if not phrase_positions:
            prefix_is_complete = False
            break
        fronted_adjuncts.append({
            "preposition": words[marker]["token"],
            "phrase": [words[i]["token"] for i in phrase_positions],
        })
        fronted_positions.add(marker)
        fronted_positions.update(phrase_positions)
        prefix_cursor = scan
    if prefix_is_complete and prefix_cursor == subject_start:
        adjuncts.extend(fronted_adjuncts)
        assigned.update(fronted_positions)

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
        object_positions = _coordinated_phrase_span(words, object_positions, cursor, len(words))
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
        "predicate_structure": _predicate_structure(words, predicate_positions, verb_pos),
        "unresolved_tokens": unresolved,
        "notes": [
            "Kerangka klausa sederhana; bukan analisis sintaksis lengkap.",
            "Frasa nominal dilaporkan sebagai rentang datar; inti dan pewatasnya belum dianalisis. Negasi verbal 'tidak' dan 'belum' dikenali secara terbatas. Penanda modalitas 'mau', 'ingin', 'hendak', dan 'bisa' (VERB), serta 'akan' (ADV), digabung ke rentang predikat hanya jika diikuti verba leksikal; penggunaan verbal tunggal tetap dipertahankan sebagai predikat. Empat ADV temporal eksplisit ('besok', 'nanti', 'sekarang', 'tadi') dapat dicatat sebagai keterangan awal sebelum subjek. Predikat nonverbal adjektival/nominal sederhana dikenali secara heuristik; modalitas lain, pelengkap, koordinasi, klausa majemuk, dan subjek tersirat belum dimodelkan.",
        ],
    }

"""Validasi struktural data Lexara Concept Layer v1 (read-only)."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, Iterable

from tools.kamus_loader import load_batch

STATUSES = {"proposed", "reviewed", "rejected"}
RELATION_TYPES = {
    "IS_A", "PART_OF", "HAS_PART", "CAUSES",
    "USED_FOR", "HAS_PROPERTY", "LOCATED_IN", "ASSOCIATED_WITH",
}
CONCEPT_ID_RE = re.compile(r"C[0-9]{6,}")
RELATION_ID_RE = re.compile(r"R[0-9]{6,}")

CONCEPT_FIELDS = {"concept_id", "label", "definition", "status", "evidence"}
MAPPING_FIELDS = {"sense_id", "concept_id", "status", "evidence"}
RELATION_FIELDS = {"relation_id", "source", "type", "target", "status", "evidence"}
EVIDENCE_FIELDS = {"source_type", "source_ref", "rationale"}


def _read_jsonl(path: str | Path, kind: str) -> tuple[list[dict[str, Any]], list[str]]:
    file_path = Path(path)
    records: list[dict[str, Any]] = []
    errors: list[str] = []
    try:
        lines = file_path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        return [], [f"{file_path}: tidak dapat dibaca sebagai UTF-8: {exc}"]

    for line_number, raw in enumerate(lines, start=1):
        location = f"{file_path}:{line_number}"
        if not raw.strip():
            errors.append(f"{location}: baris kosong tidak diizinkan")
            continue
        try:
            value = json.loads(raw)
        except json.JSONDecodeError as exc:
            errors.append(f"{location}: JSON tidak valid: {exc.msg}")
            continue
        if not isinstance(value, dict):
            errors.append(f"{location}: setiap baris harus berupa objek JSON")
            continue
        records.append(value)
    return records, errors


def _check_exact_fields(
    record: dict[str, Any], expected: set[str], location: str
) -> list[str]:
    errors: list[str] = []
    missing = expected - record.keys()
    extra = record.keys() - expected
    if missing:
        errors.append(f"{location}: field wajib hilang: {sorted(missing)}")
    if extra:
        errors.append(f"{location}: field tidak dikenal: {sorted(extra)}")
    return errors


def _check_text(value: Any, location: str) -> list[str]:
    if not isinstance(value, str) or not value.strip():
        return [f"{location}: harus berupa teks nonkosong"]
    return []


def _check_evidence(value: Any, location: str) -> list[str]:
    if not isinstance(value, dict):
        return [f"{location}: evidence harus berupa objek"]
    errors = _check_exact_fields(value, EVIDENCE_FIELDS, location)
    errors.extend(_check_text(value.get("source_type"), f"{location}.source_type"))
    source_ref = value.get("source_ref")
    if source_ref is not None and (not isinstance(source_ref, str) or not source_ref.strip()):
        errors.append(f"{location}.source_ref: harus berupa teks nonkosong atau null")
    errors.extend(_check_text(value.get("rationale"), f"{location}.rationale"))
    return errors


def _check_status(record: dict[str, Any], location: str) -> list[str]:
    status = record.get("status")
    if not isinstance(status, str) or status not in STATUSES:
        return [f"{location}.status: harus salah satu dari {sorted(STATUSES)}"]
    return []


def load_sense_ids(paths: Iterable[str | Path]) -> tuple[set[str], list[str]]:
    """Read dictionary batches without modifying them and collect actual sense IDs."""
    path_list = list(paths)
    sense_ids: set[str] = set()
    errors: list[str] = []
    for path_value in path_list:
        path = Path(path_value)
        try:
            entries = load_batch(path)
        except (OSError, ValueError) as exc:
            errors.append(f"{path}: gagal membaca indeks sense: {exc}")
            continue
        for entry_number, entry in enumerate(entries, start=1):
            senses = entry.get("senses")
            if not isinstance(senses, list):
                errors.append(f"{path}: entri[{entry_number}].senses harus berupa array")
                continue
            for sense_number, sense in enumerate(senses, start=1):
                location = f"{path}:entri[{entry_number}].senses[{sense_number}]"
                if not isinstance(sense, dict):
                    errors.append(f"{location}: sense harus berupa objek")
                    continue
                sense_id = sense.get("sense_id")
                if not isinstance(sense_id, str) or not sense_id.strip():
                    errors.append(f"{location}.sense_id: harus berupa teks nonkosong")
                    continue
                if sense_id in sense_ids:
                    errors.append(f"{location}: sense_id duplikat {sense_id}")
                sense_ids.add(sense_id)
    if not path_list:
        errors.append("minimal satu --sense-index wajib diberikan untuk resolusi sense_id")
    return sense_ids, errors


def validate_records(
    concepts: list[dict[str, Any]],
    mappings: list[dict[str, Any]],
    relations: list[dict[str, Any]],
    sense_ids: set[str],
) -> list[str]:
    """Validate parsed Concept Layer records and cross-file references."""
    errors: list[str] = []
    concept_ids: set[str] = set()
    concept_status: dict[str, str] = {}

    for index, record in enumerate(concepts, start=1):
        loc = f"concepts[{index}]"
        errors.extend(_check_exact_fields(record, CONCEPT_FIELDS, loc))
        concept_id = record.get("concept_id")
        if not isinstance(concept_id, str) or not CONCEPT_ID_RE.fullmatch(concept_id):
            errors.append(f"{loc}.concept_id: format harus C diikuti minimal enam digit")
        elif concept_id in concept_ids:
            errors.append(f"{loc}.concept_id: duplikat {concept_id}")
        else:
            concept_ids.add(concept_id)
            if record.get("status") in STATUSES:
                concept_status[concept_id] = record["status"]
        errors.extend(_check_text(record.get("label"), f"{loc}.label"))
        errors.extend(_check_text(record.get("definition"), f"{loc}.definition"))
        errors.extend(_check_status(record, loc))
        errors.extend(_check_evidence(record.get("evidence"), f"{loc}.evidence"))

    mapping_pairs: set[tuple[str, str]] = set()
    for index, record in enumerate(mappings, start=1):
        loc = f"sense_concept_map[{index}]"
        errors.extend(_check_exact_fields(record, MAPPING_FIELDS, loc))
        sense_id = record.get("sense_id")
        concept_id = record.get("concept_id")
        errors.extend(_check_text(sense_id, f"{loc}.sense_id"))
        errors.extend(_check_text(concept_id, f"{loc}.concept_id"))
        if isinstance(sense_id, str) and sense_id.strip() and sense_id not in sense_ids:
            errors.append(f"{loc}.sense_id: tidak ditemukan pada --sense-index: {sense_id}")
        if isinstance(concept_id, str) and concept_id.strip() and concept_id not in concept_ids:
            errors.append(f"{loc}.concept_id: konsep tidak ditemukan: {concept_id}")
        pair = (sense_id, concept_id)
        if all(isinstance(item, str) for item in pair):
            if pair in mapping_pairs:
                errors.append(f"{loc}: pasangan sense_id + concept_id duplikat")
            mapping_pairs.add(pair)
        errors.extend(_check_status(record, loc))
        errors.extend(_check_evidence(record.get("evidence"), f"{loc}.evidence"))

    relation_ids: set[str] = set()
    relation_keys: set[tuple[str, str, str]] = set()
    for index, record in enumerate(relations, start=1):
        loc = f"concept_relations[{index}]"
        errors.extend(_check_exact_fields(record, RELATION_FIELDS, loc))
        relation_id = record.get("relation_id")
        source = record.get("source")
        relation_type = record.get("type")
        target = record.get("target")
        if not isinstance(relation_id, str) or not RELATION_ID_RE.fullmatch(relation_id):
            errors.append(f"{loc}.relation_id: format harus R diikuti minimal enam digit")
        elif relation_id in relation_ids:
            errors.append(f"{loc}.relation_id: duplikat {relation_id}")
        else:
            relation_ids.add(relation_id)
        for field, value in (("source", source), ("target", target)):
            errors.extend(_check_text(value, f"{loc}.{field}"))
            if isinstance(value, str) and value.strip() and value not in concept_ids:
                errors.append(f"{loc}.{field}: konsep tidak ditemukan: {value}")
        if source == target and isinstance(source, str):
            errors.append(f"{loc}: relasi diri sendiri tidak diizinkan pada v1")
        if not isinstance(relation_type, str) or relation_type not in RELATION_TYPES:
            errors.append(f"{loc}.type: tipe relasi tidak dikenal: {relation_type!r}")
        key = (source, relation_type, target)
        if all(isinstance(item, str) for item in key):
            if key in relation_keys:
                errors.append(f"{loc}: kombinasi source + type + target duplikat")
            relation_keys.add(key)
        errors.extend(_check_status(record, loc))
        errors.extend(_check_evidence(record.get("evidence"), f"{loc}.evidence"))

    return errors


def validate_concept_layer(
    concepts_path: str | Path,
    mappings_path: str | Path,
    relations_path: str | Path,
    sense_index_paths: Iterable[str | Path],
) -> tuple[dict[str, int], list[str]]:
    """Validate the three JSONL files and resolve sense IDs from read-only dictionary batches."""
    sense_paths = list(sense_index_paths)
    sense_ids, errors = load_sense_ids(sense_paths)
    concepts, file_errors = _read_jsonl(concepts_path, "concepts")
    errors.extend(file_errors)
    mappings, file_errors = _read_jsonl(mappings_path, "sense_concept_map")
    errors.extend(file_errors)
    relations, file_errors = _read_jsonl(relations_path, "concept_relations")
    errors.extend(file_errors)
    errors.extend(validate_records(concepts, mappings, relations, sense_ids))
    counts = {
        "concepts": len(concepts),
        "mappings": len(mappings),
        "relations": len(relations),
        "sense_ids": len(sense_ids),
    }
    return counts, errors


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validasi struktural Lexara Concept Layer v1 (read-only)."
    )
    parser.add_argument("--concepts", required=True, type=Path, help="Path concepts.jsonl")
    parser.add_argument("--mappings", required=True, type=Path, help="Path sense_concept_map.jsonl")
    parser.add_argument("--relations", required=True, type=Path, help="Path concept_relations.jsonl")
    parser.add_argument(
        "--sense-index", required=True, action="append", type=Path,
        help="Batch kamus JSONL untuk resolusi sense_id; dapat diulang untuk beberapa batch",
    )
    args = parser.parse_args()
    counts, errors = validate_concept_layer(
        args.concepts, args.mappings, args.relations, args.sense_index
    )
    print("RINGKASAN VALIDASI CONCEPT LAYER")
    print(f"Konsep diperiksa : {counts['concepts']}")
    print(f"Pemetaan diperiksa: {counts['mappings']}")
    print(f"Relasi diperiksa : {counts['relations']}")
    print(f"Sense terindeks  : {counts['sense_ids']}")
    if errors:
        print("VALIDASI GAGAL")
        for error in errors:
            print(f"- {error}")
        return 1
    print("VALIDASI BERHASIL")
    print("Catatan: validasi struktural tidak menilai kebenaran linguistik.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

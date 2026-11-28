"""Pembaca baca-saja untuk Lexara Concept Layer v1."""
from __future__ import annotations
import json
import re
from pathlib import Path
from typing import Any

CONCEPT_FIELDS = {"concept_id", "label", "definition", "status", "evidence"}
MAPPING_FIELDS = {"sense_id", "concept_id", "status", "evidence"}
RELATION_FIELDS = {"relation_id", "source", "type", "target", "status", "evidence"}
EVIDENCE_FIELDS = {"source_type", "source_ref", "rationale"}
STATUSES = {"proposed", "reviewed", "rejected"}
RELATION_TYPES = {"IS_A", "PART_OF", "HAS_PART", "CAUSES", "USED_FOR", "HAS_PROPERTY", "LOCATED_IN", "ASSOCIATED_WITH"}
CONCEPT_ID_RE = re.compile(r"C[0-9]{6,}")
RELATION_ID_RE = re.compile(r"R[0-9]{6,}")

class ConceptLayerLoadError(ValueError):
    """Data Concept Layer tidak dapat dimuat secara aman."""

def _text(value: Any, field: str, location: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ConceptLayerLoadError(f"{location}.{field}: harus berupa teks nonkosong")

def _validate(record: dict, kind: str, location: str) -> None:
    _text(record.get("status"), "status", location)
    if record["status"] not in STATUSES:
        raise ConceptLayerLoadError(f"{location}.status: nilai tidak dikenal")
    evidence = record.get("evidence")
    if not isinstance(evidence, dict) or set(evidence) != EVIDENCE_FIELDS:
        raise ConceptLayerLoadError(f"{location}.evidence: struktur field tidak valid")
    _text(evidence.get("source_type"), "evidence.source_type", location)
    _text(evidence.get("rationale"), "evidence.rationale", location)
    ref = evidence.get("source_ref")
    if ref is not None and (not isinstance(ref, str) or not ref.strip()):
        raise ConceptLayerLoadError(f"{location}.evidence.source_ref: harus teks nonkosong atau null")
    if kind == "concepts":
        if not isinstance(record.get("concept_id"), str) or not CONCEPT_ID_RE.fullmatch(record["concept_id"]):
            raise ConceptLayerLoadError(f"{location}.concept_id: format ID tidak valid")
        _text(record.get("label"), "label", location)
        _text(record.get("definition"), "definition", location)
    elif kind == "mappings":
        _text(record.get("sense_id"), "sense_id", location)
        _text(record.get("concept_id"), "concept_id", location)
    else:
        if not isinstance(record.get("relation_id"), str) or not RELATION_ID_RE.fullmatch(record["relation_id"]):
            raise ConceptLayerLoadError(f"{location}.relation_id: format ID tidak valid")
        _text(record.get("source"), "source", location)
        _text(record.get("target"), "target", location)
        if not isinstance(record.get("type"), str) or record["type"] not in RELATION_TYPES:
            raise ConceptLayerLoadError(f"{location}.type: tipe relasi tidak dikenal")
        if record["source"] == record["target"]:
            raise ConceptLayerLoadError(f"{location}: relasi diri sendiri tidak diizinkan")

def _read(path: str | Path, kind: str, fields: set[str]) -> list[dict[str, Any]]:
    file_path = Path(path)
    try:
        lines = file_path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        raise ConceptLayerLoadError(f"{kind}: file tidak tersedia/tidak valid UTF-8: {file_path}: {exc}") from exc
    result = []
    for number, raw in enumerate(lines, 1):
        loc = f"{file_path}:{number}"
        if not raw.strip():
            raise ConceptLayerLoadError(f"{loc}: baris kosong tidak diizinkan")
        try:
            item = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ConceptLayerLoadError(f"{loc}: JSON tidak valid: {exc.msg}") from exc
        if not isinstance(item, dict):
            raise ConceptLayerLoadError(f"{loc}: setiap baris harus berupa objek JSON")
        if set(item) != fields:
            raise ConceptLayerLoadError(f"{loc}: field tidak sesuai; hilang={sorted(fields-set(item))}, tambahan={sorted(set(item)-fields)}")
        _validate(item, kind, loc)
        result.append(item)
    return result

def load_concept_layer(concepts_path: str | Path, mappings_path: str | Path, relations_path: str | Path) -> dict[str, list[dict[str, Any]]]:
    """Muat data dan ekspos hanya record reviewed yang seluruh acuannya reviewed.

    File kosong berarti data termuat tanpa record. File hilang/rusak melempar
    ConceptLayerLoadError. File sumber tidak pernah diubah.
    """
    concepts = _read(concepts_path, "concepts", CONCEPT_FIELDS)
    mappings = _read(mappings_path, "mappings", MAPPING_FIELDS)
    relations = _read(relations_path, "relations", RELATION_FIELDS)
    by_id = {}
    for item in concepts:
        cid = item["concept_id"]
        if cid in by_id:
            raise ConceptLayerLoadError(f"concept_id duplikat: {cid}")
        by_id[cid] = item
    pairs = set()
    for item in mappings:
        pair = (item["sense_id"], item["concept_id"])
        if pair in pairs:
            raise ConceptLayerLoadError(f"pasangan pemetaan duplikat: {pair}")
        pairs.add(pair)
        if item["concept_id"] not in by_id:
            raise ConceptLayerLoadError(f"pemetaan merujuk konsep yang tidak ditemukan: {item['concept_id']}")
    relation_ids, relation_keys = set(), set()
    for item in relations:
        rid = item["relation_id"]
        if rid in relation_ids:
            raise ConceptLayerLoadError(f"relation_id duplikat: {rid}")
        relation_ids.add(rid)
        key = (item["source"], item["type"], item["target"])
        if key in relation_keys:
            raise ConceptLayerLoadError(f"relasi duplikat: {key}")
        relation_keys.add(key)
        for endpoint in (item["source"], item["target"]):
            if endpoint not in by_id:
                raise ConceptLayerLoadError(f"relasi merujuk konsep yang tidak ditemukan: {endpoint}")
    active_concepts = [x for x in concepts if x["status"] == "reviewed"]
    active_ids = {x["concept_id"] for x in active_concepts}
    active_mappings = [x for x in mappings if x["status"] == "reviewed" and x["concept_id"] in active_ids]
    active_relations = [x for x in relations if x["status"] == "reviewed" and x["source"] in active_ids and x["target"] in active_ids]
    return {"concepts": active_concepts, "mappings": active_mappings, "relations": active_relations}

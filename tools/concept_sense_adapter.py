"""Adapter read-only untuk menghubungkan kandidat sense kamus ke Concept Layer."""
from __future__ import annotations

from typing import Any


class ConceptSenseAdapterError(ValueError):
    """Masukan kandidat sense atau Concept Layer tidak sesuai kontrak adapter."""


def map_sense_candidates_to_concepts(
    candidates: list[dict[str, Any]],
    concept_layer: dict[str, list[dict[str, Any]]],
) -> list[dict[str, Any]]:
    """Lampirkan konsep reviewed ke setiap kandidat sense tanpa memilih sense.

    Bentuk kandidat mengikuti keluaran lookup_token; setiap item memiliki
    metadata kecocokan dan entry yang memuat daftar senses.
    Pemetaan dan konsep yang bukan reviewed diabaikan secara defensif.
    Relasi antarkonsep tidak digunakan untuk membuat pemetaan baru.
    """
    if not isinstance(candidates, list):
        raise TypeError("candidates harus berupa list")
    if not isinstance(concept_layer, dict):
        raise TypeError("concept_layer harus berupa dictionary")
    for key in ("concepts", "mappings", "relations"):
        if key not in concept_layer or not isinstance(concept_layer[key], list):
            raise ConceptSenseAdapterError(
                f"concept_layer.{key} harus berupa list"
            )

    reviewed_concepts = {
        item["concept_id"]: item
        for item in concept_layer["concepts"]
        if isinstance(item, dict)
        and item.get("status") == "reviewed"
        and isinstance(item.get("concept_id"), str)
    }
    mappings_by_sense: dict[str, list[str]] = {}
    for mapping in concept_layer["mappings"]:
        if not isinstance(mapping, dict) or mapping.get("status") != "reviewed":
            continue
        sense_id = mapping.get("sense_id")
        concept_id = mapping.get("concept_id")
        if (
            isinstance(sense_id, str)
            and isinstance(concept_id, str)
            and concept_id in reviewed_concepts
        ):
            mappings_by_sense.setdefault(sense_id, []).append(concept_id)

    results: list[dict[str, Any]] = []
    for index, candidate in enumerate(candidates):
        if not isinstance(candidate, dict):
            raise ConceptSenseAdapterError(
                f"candidates[{index}] harus berupa dictionary"
            )
        entry = candidate.get("entry")
        if not isinstance(entry, dict):
            raise ConceptSenseAdapterError(
                f"candidates[{index}].entry harus berupa dictionary"
            )
        senses = entry.get("senses")
        if not isinstance(senses, list):
            raise ConceptSenseAdapterError(
                f"candidates[{index}].entry.senses harus berupa list"
            )

        for sense_index, sense in enumerate(senses):
            if not isinstance(sense, dict):
                raise ConceptSenseAdapterError(
                    f"candidates[{index}].entry.senses[{sense_index}] harus berupa dictionary"
                )
            sense_id = sense.get("sense_id")
            if not isinstance(sense_id, str) or not sense_id.strip():
                raise ConceptSenseAdapterError(
                    f"candidates[{index}].entry.senses[{sense_index}].sense_id harus berupa teks nonkosong"
                )
            concept_ids = mappings_by_sense.get(sense_id, [])
            results.append({
                "entry_id": candidate.get("entry_id", entry.get("id")),
                "lemma": candidate.get("lemma", entry.get("lemma")),
                "matched_form": candidate.get("matched_form"),
                "match_type": candidate.get("match_type"),
                "sense_id": sense_id,
                "sense": sense,
                "concepts": [
                    {
                        "concept_id": concept_id,
                        "label": reviewed_concepts[concept_id]["label"],
                        "definition": reviewed_concepts[concept_id]["definition"],
                    }
                    for concept_id in concept_ids
                ],
                "mapping_status": "mapped" if concept_ids else "unmapped",
            })
    return results

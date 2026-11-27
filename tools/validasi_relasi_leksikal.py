"""Validasi struktur relasi leksikal pada kamus Sistem Bahasa.

Pemeriksaan ini bersifat struktural, bukan penilaian kebenaran linguistik.
Jalankan untuk satu batch:
    python -m tools.validasi_relasi_leksikal data/kamus/batch-001.jsonl
"""
from __future__ import annotations

import argparse
import unicodedata
from pathlib import Path
from typing import Iterable

from tools.kamus_loader import load_batch


_RELATION_FIELDS = ("synonyms", "antonyms", "related_terms")


def _key(value: str) -> str:
    return unicodedata.normalize("NFC", value).strip().casefold()


def validate_entry_relations(entry: dict, source: str = "<entry>") -> list[str]:
    """Return structural relation errors for one already-loaded dictionary entry."""
    errors: list[str] = []
    lemma = entry.get("lemma")
    if not isinstance(lemma, str) or not lemma.strip():
        return [f"{source}: lemma harus berupa teks nonkosong untuk validasi relasi"]

    lemma_key = _key(lemma)

    def check_relation_fields(container: dict, location: str) -> None:
        for field in _RELATION_FIELDS:
            if field not in container:
                continue
            values = container[field]
            if not isinstance(values, list):
                errors.append(f"{location}: {field} harus berupa array")
                continue

            seen: set[str] = set()
            for index, value in enumerate(values):
                item_location = f"{location}.{field}[{index}]"
                if not isinstance(value, str) or not value.strip():
                    errors.append(f"{item_location}: nilai harus berupa teks nonkosong")
                    continue
                normalized = _key(value)
                if normalized in seen:
                    errors.append(f"{item_location}: relasi duplikat setelah normalisasi")
                else:
                    seen.add(normalized)
                if normalized == lemma_key:
                    errors.append(f"{item_location}: relasi tidak boleh menunjuk ke lemma sendiri")

    check_relation_fields(entry, source)

    if "senses" not in entry:
        return errors
    senses = entry["senses"]
    if not isinstance(senses, list):
        errors.append(f"{source}.senses: harus berupa array")
        return errors

    for index, sense in enumerate(senses):
        location = f"{source}.senses[{index}]"
        if not isinstance(sense, dict):
            errors.append(f"{location}: sense harus berupa objek")
            continue
        if any(field in sense for field in _RELATION_FIELDS):
            sense_id = sense.get("sense_id")
            if not isinstance(sense_id, str) or not sense_id.strip():
                errors.append(
                    f"{location}: sense_id wajib berupa teks nonkosong "
                    "ketika relasi per-sense digunakan"
                )
        check_relation_fields(sense, location)

    return errors


def validate_entries_relations(entries: Iterable[dict]) -> list[str]:
    """Validate relations in entries and return all structural errors."""
    errors: list[str] = []
    for index, entry in enumerate(entries, start=1):
        if not isinstance(entry, dict):
            errors.append(f"entri[{index}]: harus berupa objek")
            continue
        entry_id = entry.get("id", f"entri[{index}]")
        errors.extend(validate_entry_relations(entry, str(entry_id)))
    return errors


def validate_relation_batch(path: str | Path) -> tuple[int, list[str]]:
    """Load and validate one batch without modifying source data."""
    entries = load_batch(path)
    return len(entries), validate_entries_relations(entries)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validasi struktur relasi leksikal pada satu batch kamus."
    )
    parser.add_argument("batch", type=Path, help="Path ke satu file batch JSONL")
    args = parser.parse_args()

    try:
        entry_count, errors = validate_relation_batch(args.batch)
    except (OSError, ValueError) as exc:
        parser.exit(1, f"VALIDASI RELASI GAGAL: {exc}\n")

    if errors:
        print("VALIDASI RELASI GAGAL")
        for error in errors:
            print(f"- {error}")
        return 1

    print("VALIDASI RELASI BERHASIL")
    print(f"Entri diperiksa : {entry_count}")
    print("Pemeriksaan     : tipe array, teks nonkosong, duplikasi,")
    print("                  relasi terhadap lemma sendiri, dan sense_id")
    print("Catatan         : hasil ini hanya validasi struktur, bukan makna.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

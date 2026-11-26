"""Read-only JSONL loader for the Sistem Bahasa dictionary."""
from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path
from typing import Iterable


_REQUIRED_FIELDS = {"id", "lemma", "pos", "senses", "register"}
_ID_RE = re.compile(r"K\d{4}")


class DictionaryFormatError(ValueError):
    """Raised when a dictionary batch does not follow the expected format."""


def _normalized_key(value: str) -> str:
    return unicodedata.normalize("NFC", value).strip().casefold()


def load_batch(path: str | Path) -> list[dict]:
    """Load one JSONL batch without modifying its entries."""
    batch_path = Path(path)
    entries: list[dict] = []

    try:
        lines = batch_path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise DictionaryFormatError(f"Tidak dapat membaca {batch_path}: {exc}") from exc

    for line_number, raw_line in enumerate(lines, start=1):
        if not raw_line.strip():
            raise DictionaryFormatError(
                f"{batch_path}:{line_number}: baris kosong tidak diizinkan"
            )

        try:
            item = json.loads(raw_line)
        except json.JSONDecodeError as exc:
            raise DictionaryFormatError(
                f"{batch_path}:{line_number}: JSON tidak valid: {exc.msg}"
            ) from exc

        if not isinstance(item, dict):
            raise DictionaryFormatError(
                f"{batch_path}:{line_number}: setiap baris harus berupa objek JSON"
            )

        missing = _REQUIRED_FIELDS - item.keys()
        if missing:
            raise DictionaryFormatError(
                f"{batch_path}:{line_number}: field wajib hilang: {sorted(missing)}"
            )

        entry_id = item["id"]
        if not isinstance(entry_id, str) or not _ID_RE.fullmatch(entry_id):
            raise DictionaryFormatError(
                f"{batch_path}:{line_number}: ID harus berformat K0001"
            )

        lemma = item["lemma"]
        if not isinstance(lemma, str) or not lemma.strip():
            raise DictionaryFormatError(
                f"{batch_path}:{line_number}: lemma harus berupa teks nonkosong"
            )

        for field in ("pos", "senses", "register"):
            value = item[field]
            if not isinstance(value, list) or not value:
                raise DictionaryFormatError(
                    f"{batch_path}:{line_number}: {field} harus berupa array tidak kosong"
                )

        entries.append(item)

    return entries


def load_dictionary(paths: Iterable[str | Path]) -> list[dict]:
    """Load multiple batches and reject duplicate IDs or normalized lemmas."""
    all_entries: list[dict] = []
    seen_ids: dict[str, str] = {}
    seen_lemmas: dict[str, str] = {}

    for path_value in paths:
        path = Path(path_value)
        batch_entries = load_batch(path)

        for line_number, entry in enumerate(batch_entries, start=1):
            entry_id = entry["id"]
            lemma_key = _normalized_key(entry["lemma"])
            source = f"{path}:{line_number}"

            if entry_id in seen_ids:
                raise DictionaryFormatError(
                    f"{source}: ID duplikat {entry_id}, juga ada di {seen_ids[entry_id]}"
                )
            if lemma_key in seen_lemmas:
                raise DictionaryFormatError(
                    f"{source}: lemma duplikat {entry['lemma']!r}, "
                    f"juga ada di {seen_lemmas[lemma_key]}"
                )

            seen_ids[entry_id] = source
            seen_lemmas[lemma_key] = source
            all_entries.append(entry)

    return all_entries


def load_dictionary_directory(directory: str | Path) -> list[dict]:
    """Load all batch-NNN.jsonl files in a directory in filename order."""
    data_dir = Path(directory)
    batch_paths = sorted(data_dir.glob("batch-[0-9][0-9][0-9].jsonl"))
    if not batch_paths:
        raise DictionaryFormatError(
            f"Tidak ditemukan file batch-NNN.jsonl di {data_dir}"
        )
    return load_dictionary(batch_paths)

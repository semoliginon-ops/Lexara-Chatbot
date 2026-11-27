"""Audit index kamus terhadap sumber batch secara streaming per batch.

Jalankan dari root repository:
    python -m tools.audit_index_kamus
"""
from __future__ import annotations

import argparse
import json
import re
import unicodedata
from collections import Counter
from pathlib import Path

from tools.kamus_loader import DictionaryFormatError, load_batch


SHARDS = {
    "a-c": set("abc"),
    "d-f": set("def"),
    "g-i": set("ghi"),
    "j-l": set("jkl"),
    "m-o": set("mno"),
    "p-r": set("pqr"),
    "s-u": set("stu"),
    "v-z": set("vwxyz"),
}
VALID_TYPES = {"lemma", "variant", "derived_form"}
ID_PATTERN = re.compile(r"K\d{4}")
BATCH_PATTERN = re.compile(r"batch-\d{3}")


class IndexAuditError(ValueError):
    """Raised when the index cannot be audited."""


def _normalized(value: str) -> str:
    return unicodedata.normalize("NFC", value).casefold()


def _read_index(index_dir: Path) -> tuple[Counter, list[str]]:
    rows: Counter = Counter()
    errors: list[str] = []

    for shard, allowed_letters in SHARDS.items():
        path = index_dir / f"{shard}.tsv"
        if not path.is_file():
            errors.append(f"Shard tidak ditemukan: {path}")
            continue

        previous_token: str | None = None
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except OSError as exc:
            errors.append(f"Tidak dapat membaca {path}: {exc}")
            continue

        for line_number, line in enumerate(lines, start=1):
            if not line or line.startswith("#"):
                continue
            columns = line.split("\t")
            if len(columns) != 5:
                errors.append(
                    f"{path}:{line_number}: harus ada 5 kolom, ditemukan {len(columns)}"
                )
                continue

            token, entry_id, lemma, match_type, batch_name = columns
            if not token or not lemma:
                errors.append(f"{path}:{line_number}: token/lemma kosong")
                continue
            if not ID_PATTERN.fullmatch(entry_id):
                errors.append(f"{path}:{line_number}: ID tidak valid: {entry_id}")
            if match_type not in VALID_TYPES:
                errors.append(f"{path}:{line_number}: tipe tidak dikenal: {match_type}")
            if not BATCH_PATTERN.fullmatch(batch_name):
                errors.append(f"{path}:{line_number}: nama batch tidak valid: {batch_name}")

            first_letter = _normalized(token)[:1]
            if first_letter not in allowed_letters:
                errors.append(
                    f"{path}:{line_number}: token {token!r} salah shard"
                )

            sort_key = _normalized(token)
            if previous_token is not None and sort_key < previous_token:
                errors.append(f"{path}:{line_number}: urutan token tidak alfabetis")
            previous_token = sort_key
            rows[(token, entry_id, lemma, match_type, batch_name)] += 1

    return rows, errors


def audit_index(
    data_dir: str | Path,
    index_dir: str | Path,
    expected_batches: int = 60,
    expected_entries: int = 3000,
) -> dict:
    """Compare all index rows with batch source files, loading one batch at a time."""
    data_path = Path(data_dir)
    index_path = Path(index_dir)
    batch_paths = sorted(data_path.glob("batch-[0-9][0-9][0-9].jsonl"))
    errors: list[str] = []

    if len(batch_paths) != expected_batches:
        errors.append(
            f"Jumlah batch tidak sesuai: ditemukan {len(batch_paths)}, "
            f"seharusnya {expected_batches}"
        )

    expected: Counter = Counter()
    seen_ids: set[str] = set()
    seen_lemmas: set[str] = set()
    entry_count = 0

    for batch_path in batch_paths:
        try:
            entries = load_batch(batch_path)
        except (DictionaryFormatError, OSError) as exc:
            errors.append(str(exc))
            continue

        batch_name = batch_path.stem
        for entry in entries:
            entry_count += 1
            entry_id = entry["id"]
            lemma = entry["lemma"]
            lemma_key = _normalized(lemma)

            if entry_id in seen_ids:
                errors.append(f"ID duplikat pada sumber batch: {entry_id}")
            seen_ids.add(entry_id)
            if lemma_key in seen_lemmas:
                errors.append(f"Lema duplikat pada sumber batch: {lemma}")
            seen_lemmas.add(lemma_key)

            expected[(lemma, entry_id, lemma, "lemma", batch_name)] += 1

            for field, match_type in (
                ("variants", "variant"),
                ("derived_forms", "derived_form"),
            ):
                forms = entry.get(field, [])
                if not isinstance(forms, list):
                    errors.append(
                        f"{batch_name}/{entry_id}: field {field} harus berupa array"
                    )
                    continue
                for form in forms:
                    if not isinstance(form, str) or not form.strip():
                        errors.append(
                            f"{batch_name}/{entry_id}: bentuk kosong/tidak valid pada {field}"
                        )
                        continue
                    expected[(form, entry_id, lemma, match_type, batch_name)] += 1

    if entry_count != expected_entries:
        errors.append(
            f"Jumlah lema tidak sesuai: ditemukan {entry_count}, "
            f"seharusnya {expected_entries}"
        )

    actual, index_errors = _read_index(index_path)
    errors.extend(index_errors)
    required_lemmas = Counter(
        {row: count for row, count in expected.items() if row[3] == "lemma"}
    )
    missing_lemmas = required_lemmas - actual
    extra = actual - expected
    optional_expected = expected - required_lemmas
    omitted_optional = optional_expected - actual

    return {
        "ok": not errors and not missing_lemmas and not extra,
        "batch_count": len(batch_paths),
        "entry_count": entry_count,
        "expected_rows": sum(expected.values()),
        "actual_rows": sum(actual.values()),
        "missing_lemma_rows": list(missing_lemmas.items()),
        "omitted_optional_rows": list(omitted_optional.items()),
        "extra_rows": list(extra.items()),
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Cocokkan delapan shard index dengan sumber batch JSONL."
    )
    parser.add_argument("--data-dir", type=Path, default=Path("data/kamus"))
    parser.add_argument("--index-dir", type=Path, default=Path("data/kamus/index"))
    parser.add_argument("--expected-batches", type=int, default=60)
    parser.add_argument("--expected-entries", type=int, default=3000)
    args = parser.parse_args()

    try:
        report = audit_index(
            args.data_dir,
            args.index_dir,
            expected_batches=args.expected_batches,
            expected_entries=args.expected_entries,
        )
    except (OSError, IndexAuditError) as exc:
        parser.exit(1, f"AUDIT GAGAL: {exc}\n")

    print("AUDIT INDEX BERHASIL" if report["ok"] else "AUDIT INDEX GAGAL")
    print(f"Batch sumber       : {report['batch_count']}")
    print(f"Lema sumber        : {report['entry_count']}")
    print(f"Baris yang diharap : {report['expected_rows']}")
    print(f"Baris pada index   : {report['actual_rows']}")
    print(f"Lema index hilang  : {len(report['missing_lemma_rows'])}")
    print(f"Baris opsional tak diindeks: {len(report['omitted_optional_rows'])}")
    print(f"Baris index tak cocok: {len(report['extra_rows'])}")
    print(f"Kesalahan struktur : {len(report['errors'])}")

    for label, differences in (
        ("LEMA HILANG", report["missing_lemma_rows"]),
        ("BARIS TAK COCOK", report["extra_rows"]),
    ):
        for row, count in differences[:20]:
            print(f"{label}: {row} (jumlah {count})")
    for error in report["errors"][:20]:
        print(f"ERROR: {error}")

    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

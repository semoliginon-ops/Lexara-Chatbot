"""Validasi loader terhadap seluruh kamus Sistem Bahasa.

Jalankan dari root repository:
    python -m tools.validasi_kamus_lengkap
"""
from __future__ import annotations

import argparse
from pathlib import Path

from tools.kamus_loader import (
    DictionaryFormatError,
    load_dictionary_directory,
)


def validate_full_dictionary(
    directory: str | Path,
    expected_batches: int = 60,
    expected_entries: int = 3000,
) -> tuple[int, int]:
    """Load every batch and verify the expected corpus size."""
    data_dir = Path(directory)
    batch_paths = sorted(data_dir.glob("batch-[0-9][0-9][0-9].jsonl"))

    if len(batch_paths) != expected_batches:
        raise DictionaryFormatError(
            f"Jumlah batch tidak sesuai: ditemukan {len(batch_paths)}, "
            f"seharusnya {expected_batches}"
        )

    entries = load_dictionary_directory(data_dir)
    if len(entries) != expected_entries:
        raise DictionaryFormatError(
            f"Jumlah entri tidak sesuai: ditemukan {len(entries)}, "
            f"seharusnya {expected_entries}"
        )

    return len(batch_paths), len(entries)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validasi loader terhadap seluruh batch kamus."
    )
    parser.add_argument(
        "--directory",
        type=Path,
        default=Path("data/kamus"),
        help="Folder berisi batch-NNN.jsonl (default: data/kamus)",
    )
    parser.add_argument("--expected-batches", type=int, default=60)
    parser.add_argument("--expected-entries", type=int, default=3000)
    args = parser.parse_args()

    try:
        batch_count, entry_count = validate_full_dictionary(
            args.directory,
            expected_batches=args.expected_batches,
            expected_entries=args.expected_entries,
        )
    except (DictionaryFormatError, OSError) as exc:
        parser.exit(1, f"VALIDASI GAGAL: {exc}\n")

    print("VALIDASI BERHASIL")
    print(f"Batch dimuat : {batch_count}")
    print(f"Entri dimuat : {entry_count}")
    print("Pemeriksaan  : JSONL, field wajib, format ID, array wajib,")
    print("               ID duplikat, dan lema duplikat.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

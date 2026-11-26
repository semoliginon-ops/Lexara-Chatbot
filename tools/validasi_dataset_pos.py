"""Validasi struktur dan konsistensi dataset kalimat berlabel POS.

Jalankan dari root repository:
    python -m tools.validasi_dataset_pos
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from tools.tokenizer import tokenize

POS_LABELS = {
    "NOUN", "VERB", "ADJ", "ADV", "PRON",
    "NUM", "PREP", "CONJ", "INTJ", "PART",
}
GOLD_STATUSES = {
    "resolved", "ambiguous", "unknown",
    "requires_morphology", "not_applicable",
}
SPLITS = {"development", "test"}
_ID_PATTERN = re.compile(r"^pos_\d{4}$")


class PosDatasetFormatError(ValueError):
    """Raised when a POS dataset record violates the documented schema."""


def _fail(line_number: int, message: str) -> None:
    raise PosDatasetFormatError(f"baris {line_number}: {message}")


def validate_pos_dataset(path: str | Path) -> dict[str, int]:
    """Validate JSONL records and exact token alignment with project tokenizer."""
    dataset_path = Path(path)
    sentence_count = 0
    token_count = 0
    split_counts = {"development": 0, "test": 0}
    seen_ids: set[str] = set()

    with dataset_path.open("r", encoding="utf-8") as source:
        for line_number, raw_line in enumerate(source, start=1):
            if not raw_line.strip():
                _fail(line_number, "baris kosong tidak diizinkan")
            try:
                record = json.loads(raw_line)
            except json.JSONDecodeError as exc:
                _fail(line_number, f"JSON tidak valid: {exc.msg}")

            if not isinstance(record, dict):
                _fail(line_number, "setiap record harus berupa objek JSON")

            required = {"id", "split", "text", "tokens", "phenomena", "notes"}
            missing = required - record.keys()
            if missing:
                _fail(line_number, f"field wajib hilang: {', '.join(sorted(missing))}")

            record_id = record["id"]
            if not isinstance(record_id, str) or not _ID_PATTERN.fullmatch(record_id):
                _fail(line_number, "id harus mengikuti format pos_NNNN")
            if record_id in seen_ids:
                _fail(line_number, f"id duplikat: {record_id}")
            seen_ids.add(record_id)

            split = record["split"]
            if not isinstance(split, str) or split not in SPLITS:
                _fail(line_number, "split harus development atau test")
            split_counts[split] += 1

            text = record["text"]
            if not isinstance(text, str) or not text.strip():
                _fail(line_number, "text harus berupa string tidak kosong")

            annotated_tokens = record["tokens"]
            if not isinstance(annotated_tokens, list):
                _fail(line_number, "tokens harus berupa array")
            expected_tokens = tokenize(text)
            actual_tokens = []
            for token_index, annotation in enumerate(annotated_tokens, start=1):
                if not isinstance(annotation, dict):
                    _fail(line_number, f"tokens[{token_index}] harus berupa objek")
                for field in ("token", "gold_pos", "gold_status"):
                    if field not in annotation:
                        _fail(line_number, f"tokens[{token_index}] kehilangan field {field}")
                token = annotation["token"]
                if not isinstance(token, str):
                    _fail(line_number, f"tokens[{token_index}].token harus berupa string")
                actual_tokens.append(token)

                status = annotation["gold_status"]
                label = annotation["gold_pos"]
                if not isinstance(status, str) or status not in GOLD_STATUSES:
                    _fail(line_number, f"status gold tidak dikenal pada token {token_index}")
                if label is not None and (not isinstance(label, str) or label not in POS_LABELS):
                    _fail(line_number, f"label POS tidak resmi pada token {token_index}")

                if status == "resolved" and label is None:
                    _fail(line_number, f"token resolved harus memiliki gold_pos (token {token_index})")
                if status in {"ambiguous", "unknown", "not_applicable"} and label is not None:
                    _fail(line_number, f"status {status} harus memiliki gold_pos null (token {token_index})")
                if status == "not_applicable" and token and any(ch.isalnum() for ch in token):
                    _fail(line_number, f"token kata tidak boleh not_applicable (token {token_index})")

            if actual_tokens != expected_tokens:
                _fail(
                    line_number,
                    f"token tidak cocok dengan tokenizer; diharapkan {expected_tokens!r}, "
                    f"ditemukan {actual_tokens!r}",
                )

            phenomena = record["phenomena"]
            if not isinstance(phenomena, list) or not all(
                isinstance(item, str) and item for item in phenomena
            ):
                _fail(line_number, "phenomena harus berupa array string")
            if not isinstance(record["notes"], str):
                _fail(line_number, "notes harus berupa string")

            sentence_count += 1
            token_count += len(annotated_tokens)

    if sentence_count == 0:
        raise PosDatasetFormatError("dataset tidak memiliki record")
    return {
        "sentences": sentence_count,
        "tokens": token_count,
        "development": split_counts["development"],
        "test": split_counts["test"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validasi dataset kalimat berlabel POS."
    )
    parser.add_argument(
        "--file",
        type=Path,
        default=Path("data/dataset_pos/kalimat_pos_v1.jsonl"),
        help="File JSONL dataset POS.",
    )
    args = parser.parse_args()
    try:
        result = validate_pos_dataset(args.file)
    except (PosDatasetFormatError, OSError) as exc:
        parser.exit(1, f"VALIDASI DATASET POS GAGAL: {exc}\n")

    print("VALIDASI DATASET POS BERHASIL")
    print(f"Kalimat       : {result['sentences']}")
    print(f"Token         : {result['tokens']}")
    print(f"Development   : {result['development']}")
    print(f"Test          : {result['test']}")
    print("Pemeriksaan   : JSONL, ID, split, label POS, status anotasi,")
    print("                dan kecocokan token dengan tokenizer.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

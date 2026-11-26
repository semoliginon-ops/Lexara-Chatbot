#!/usr/bin/env python3
"""Read-only structural audit for the Sistem Bahasa lexical dictionary."""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import unicodedata
from pathlib import Path

REGISTERS = {"formal", "neutral", "informal", "slang", "regional", "technical", "archaic"}
TOKEN_TYPES = {"lemma", "variant", "derived_form"}
SHARDS = ("a-c", "d-f", "g-i", "j-l", "m-o", "p-r", "s-u", "v-z")
REQUIRED = {"id", "lemma", "pos", "senses", "register"}


def norm(value: str) -> str:
    return unicodedata.normalize("NFC", value).strip().casefold()


def load_pos_codes(doc_path: Path) -> set[str]:
    text = doc_path.read_text(encoding="utf-8")
    codes = set(re.findall(r"^\|\s*([A-Z]+)\s*\|", text, flags=re.MULTILINE))
    if len(codes) != 10:
        raise ValueError(f"Dokumen kamus harus mendefinisikan tepat 10 kode POS; ditemukan {len(codes)}: {sorted(codes)}")
    return codes


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--docs", type=Path, required=True)
    parser.add_argument("--index", type=Path, required=True)
    parser.add_argument("--data-dir", type=Path, required=True)
    args = parser.parse_args()

    errors: list[str] = []
    warnings: list[str] = []
    try:
        allowed_pos = load_pos_codes(args.docs)
    except Exception as exc:
        print(f"FAIL: tidak dapat membaca 10 POS dari dokumen: {exc}")
        return 1

    batch_files = sorted(args.data_dir.glob("batch-*.jsonl"))
    if not batch_files:
        errors.append("Tidak ditemukan file batch-*.jsonl.")

    entries: list[dict] = []
    ids: dict[str, str] = {}
    lemmas: dict[str, str] = {}
    sense_ids: dict[str, str] = {}
    expected_tokens: dict[str, dict] = {}
    batch_counts: dict[str, int] = {}
    id_numbers: list[int] = []

    for batch_path in batch_files:
        match = re.fullmatch(r"batch-(\d{3})\.jsonl", batch_path.name)
        if not match:
            errors.append(f"Nama file batch tidak sesuai pola: {batch_path.name}")
            continue
        batch_name = batch_path.stem
        count = 0
        for line_no, raw in enumerate(batch_path.read_text(encoding="utf-8").splitlines(), 1):
            if not raw.strip():
                errors.append(f"{batch_path}:{line_no}: baris kosong tidak diizinkan.")
                continue
            try:
                item = json.loads(raw)
            except json.JSONDecodeError as exc:
                errors.append(f"{batch_path}:{line_no}: JSON tidak valid ({exc.msg}).")
                continue
            count += 1
            if not isinstance(item, dict):
                errors.append(f"{batch_path.name}:{line_no}: setiap baris harus berupa objek JSON.")
                continue
            entries.append(item)
            where = f"{batch_path.name}:{line_no}"

            missing = REQUIRED - item.keys()
            if missing:
                errors.append(f"{where}: field wajib hilang: {sorted(missing)}.")
                continue

            entry_id = item["id"]
            lemma = item["lemma"]
            if not isinstance(entry_id, str) or not re.fullmatch(r"K\d{4}", entry_id):
                errors.append(f"{where}: ID harus berformat K0001.")
                continue
            if entry_id in ids:
                errors.append(f"{where}: ID duplikat {entry_id}, juga ada di {ids[entry_id]}.")
            else:
                ids[entry_id] = where
                id_numbers.append(int(entry_id[1:]))

            if not isinstance(lemma, str) or not lemma.strip():
                errors.append(f"{where}: lemma harus berupa teks nonkosong.")
                continue
            if lemma != unicodedata.normalize("NFC", lemma) or lemma != lemma.strip():
                errors.append(f"{where}: lemma belum NFC atau memiliki spasi tepi.")
            lemma_key = norm(lemma)
            if lemma_key in lemmas:
                errors.append(f"{where}: lemma duplikat '{lemma}' dengan {lemmas[lemma_key]}.")
            else:
                lemmas[lemma_key] = where

            pos_values = item["pos"]
            if not isinstance(pos_values, list) or not pos_values:
                errors.append(f"{where}: pos harus berupa array tidak kosong.")
            else:
                for pos in pos_values:
                    if pos not in allowed_pos:
                        errors.append(f"{where}: kode POS tidak dikenal '{pos}'.")

            registers = item["register"]
            if not isinstance(registers, list) or not registers:
                errors.append(f"{where}: register harus berupa array tidak kosong.")
            else:
                for register in registers:
                    if register not in REGISTERS:
                        errors.append(f"{where}: register tidak dikenal '{register}'.")

            senses = item["senses"]
            if not isinstance(senses, list) or not senses:
                errors.append(f"{where}: minimal harus ada satu sense.")
            else:
                for sense in senses:
                    if not isinstance(sense, dict) or not sense.get("sense_id") or not isinstance(sense.get("definition"), str) or not sense["definition"].strip():
                        errors.append(f"{where}: setiap sense wajib memiliki sense_id dan definition.")
                        continue
                    sid = sense["sense_id"]
                    if sid in sense_ids:
                        errors.append(f"{where}: sense_id duplikat '{sid}'.")
                    else:
                        sense_ids[sid] = where
                    if "pos" in sense and sense["pos"] not in allowed_pos:
                        errors.append(f"{where}: POS pada sense tidak dikenal '{sense['pos']}'.")

            for field, token_type in (("lemma", "lemma"), ("variants", "variant"), ("derived_forms", "derived_form")):
                values = [lemma] if field == "lemma" else item.get(field, [])
                if not isinstance(values, list):
                    errors.append(f"{where}: {field} harus berupa array.")
                    continue
                for value in values:
                    if not isinstance(value, str) or not value.strip():
                        errors.append(f"{where}: token kosong/tidak valid pada {field}.")
                        continue
                    if value != unicodedata.normalize("NFC", value) or value != value.strip():
                        errors.append(f"{where}: token '{value}' belum NFC atau memiliki spasi tepi.")
                    key = norm(value)
                    record = {"id": entry_id, "lemma": lemma, "type": token_type, "batch": batch_name}
                    if key in expected_tokens:
                        previous = expected_tokens[key]
                        if previous != record:
                            errors.append(f"{where}: tabrakan token '{value}' dengan {previous['id']} ({previous['type']}).")
                    else:
                        expected_tokens[key] = record

        batch_counts[batch_name] = count

    # Historical ID gaps are reported but do not fail the audit.
    if id_numbers:
        gaps = sorted(set(range(min(id_numbers), max(id_numbers) + 1)) - set(id_numbers))
        if gaps:
            warnings.append("Celah ID (tidak otomatis dianggap kesalahan): " + ", ".join(f"K{x:04d}" for x in gaps))

    actual_tokens: dict[str, dict] = {}
    shard_counts: dict[str, int] = {}
    for shard in SHARDS:
        path = args.data_dir / "index" / f"{shard}.tsv"
        if not path.exists():
            errors.append(f"Shard index hilang: {path}.")
            continue
        rows = path.read_text(encoding="utf-8").splitlines()
        if len(rows) < 2 or not rows[0].startswith("# Token index —") or rows[1] != "# token\\tid\\tlemma\\ttype\\tbatch":
            errors.append(f"Header shard tidak valid: {path}.")
        count = 0
        seen_order: list[str] = []
        for line_no, row in enumerate(rows[2:], 3):
            if not row:
                continue
            cells = row.split("\t")
            if len(cells) != 5:
                errors.append(f"{path}:{line_no}: harus memiliki 5 kolom TSV.")
                continue
            token, entry_id, lemma, token_type, batch_name = cells
            key = norm(token)
            count += 1
            seen_order.append(key)
            if token_type not in TOKEN_TYPES:
                errors.append(f"{path}:{line_no}: tipe token tidak dikenal '{token_type}'.")
            if key in actual_tokens:
                errors.append(f"{path}:{line_no}: token index duplikat '{token}'.")
            else:
                actual_tokens[key] = {"id": entry_id, "lemma": lemma, "type": token_type, "batch": batch_name}
        if seen_order != sorted(seen_order):
            errors.append(f"Token dalam shard {path.name} tidak terurut alfabetis.")
        shard_counts[shard] = count

    for token in sorted(set(expected_tokens) - set(actual_tokens)):
        errors.append(f"Token kamus tidak ada di index: '{token}'.")
    for token in sorted(set(actual_tokens) - set(expected_tokens)):
        errors.append(f"Token index tidak punya sumber batch: '{token}'.")
    for token in sorted(set(expected_tokens) & set(actual_tokens)):
        if expected_tokens[token] != actual_tokens[token]:
            errors.append(f"Mapping index berbeda untuk '{token}': sumber={expected_tokens[token]}, index={actual_tokens[token]}.")

    index_text = args.index.read_text(encoding="utf-8")
    approved_match = re.search(r"\*\*Disetujui:\*\*\s*(\d+)\s+lemma", index_text)
    token_match = re.search(r"\*\*Token terindeks:\*\*\s*(\d+)", index_text)
    if not approved_match or int(approved_match.group(1)) != len(entries):
        errors.append(f"Angka Disetujui di INDEX harus {len(entries)}.")
    if not token_match or int(token_match.group(1)) != len(expected_tokens):
        errors.append(f"Angka Token terindeks di INDEX harus {len(expected_tokens)}.")
    for shard, count in shard_counts.items():
        pattern = rf"\|\s*{re.escape(shard)}\s*\|[^\n]*?—\s*(\d+)\s+token"
        found = re.search(pattern, index_text)
        if not found or int(found.group(1)) != count:
            errors.append(f"Jumlah token shard {shard} di INDEX harus {count}.")
    if batch_counts:
        latest = max(int(name[-3:]) for name in batch_counts)
        if not re.search(rf"\*\*Batch aktif:\*\*\s*001[–-]{latest:03d}\b", index_text):
            errors.append(f"Rentang Batch aktif di INDEX harus 001–{latest:03d}.")

    report_lines = [
        "# Dictionary Audit",
        "",
        f"- Status: **{'FAIL' if errors else 'PASS'}**",
        f"- POS resmi dari docs/KAMUS.md: {len(allowed_pos)} ({', '.join(sorted(allowed_pos))})",
        f"- Batch files: {len(batch_files)}",
        f"- Entri: {len(entries)}",
        f"- ID unik: {len(ids)}",
        f"- Lemma unik: {len(lemmas)}",
        f"- Token sumber: {len(expected_tokens)}",
        f"- Token index: {len(actual_tokens)}",
        f"- Shard: {sum(shard_counts.values())} baris",
        f"- Errors: {len(errors)}",
        f"- Warnings: {len(warnings)}",
        "",
    ]
    if warnings:
        report_lines += ["## Warnings", *[f"- {item}" for item in warnings], ""]
    if errors:
        report_lines += ["## Errors", *[f"- {item}" for item in errors[:200]], ""]
        if len(errors) > 200:
            report_lines.append(f"- ... {len(errors) - 200} error lainnya tidak ditampilkan.")
    report = "\n".join(report_lines)
    print(report)
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_path:
        with open(summary_path, "a", encoding="utf-8") as handle:
            handle.write(report + "\n")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())

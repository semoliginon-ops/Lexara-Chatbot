"""Validasi struktural metadata valensi per-sense.

Data lama tanpa valency_frames tetap diterima. Pemeriksaan ini tidak
menilai kebenaran anotasi linguistik.
"""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable

from tools.kamus_loader import load_batch

_SYNTACTIC_ROLES = {"SUBJ", "OBJ", "COMP", "OBL"}
_SEMANTIC_ROLES = {
    "AGENT", "CAUSER", "EXPERIENCER", "THEME", "PATIENT",
    "RECIPIENT", "BENEFICIARY", "INSTRUMENT", "LOCATION",
    "SOURCE", "GOAL", "RESULT", "CONTENT", "STIMULUS",
}
_REALIZATION_TYPES = {"NP", "PP", "ADJP", "CLAUSE"}
_FRAME_FIELDS = {"frame_id", "arguments"}
_ARGUMENT_FIELDS = {
    "argument_id", "syntactic_role", "semantic_role", "required", "realizations"
}
_REALIZATION_FIELDS = {"type", "prepositions"}


def _text(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _unknown_fields(value: dict, allowed: set[str], location: str) -> list[str]:
    unknown = sorted(set(value) - allowed)
    return [f"{location}: field tidak dikenal: {', '.join(unknown)}"] if unknown else []


def validate_entry_valency(entry: dict, source: str = "<entry>") -> list[str]:
    """Return structural valency errors for one already-loaded entry."""
    errors: list[str] = []
    senses = entry.get("senses")
    if not isinstance(senses, list):
        return errors

    for si, sense in enumerate(senses):
        sloc = f"{source}.senses[{si}]"
        if not isinstance(sense, dict) or "valency_frames" not in sense:
            continue
        if not _text(sense.get("sense_id")):
            errors.append(f"{sloc}: sense_id wajib berupa teks nonkosong ketika valency_frames digunakan")

        frames = sense["valency_frames"]
        if not isinstance(frames, list) or not frames:
            errors.append(f"{sloc}.valency_frames: harus berupa array tidak kosong")
            continue

        seen_frames: set[str] = set()
        for fi, frame in enumerate(frames):
            floc = f"{sloc}.valency_frames[{fi}]"
            if not isinstance(frame, dict):
                errors.append(f"{floc}: frame harus berupa objek")
                continue
            errors.extend(_unknown_fields(frame, _FRAME_FIELDS, floc))
            fid = frame.get("frame_id")
            if not _text(fid):
                errors.append(f"{floc}.frame_id: harus berupa teks nonkosong")
            elif fid in seen_frames:
                errors.append(f"{floc}.frame_id: duplikat dalam satu sense")
            else:
                seen_frames.add(fid)

            arguments = frame.get("arguments")
            if not isinstance(arguments, list) or not arguments:
                errors.append(f"{floc}.arguments: harus berupa array tidak kosong")
                continue

            seen_arguments: set[str] = set()
            for ai, argument in enumerate(arguments):
                aloc = f"{floc}.arguments[{ai}]"
                if not isinstance(argument, dict):
                    errors.append(f"{aloc}: argumen harus berupa objek")
                    continue
                errors.extend(_unknown_fields(argument, _ARGUMENT_FIELDS, aloc))
                aid = argument.get("argument_id")
                if not _text(aid):
                    errors.append(f"{aloc}.argument_id: harus berupa teks nonkosong")
                elif aid in seen_arguments:
                    errors.append(f"{aloc}.argument_id: duplikat dalam satu frame")
                else:
                    seen_arguments.add(aid)

                sr = argument.get("syntactic_role")
                if not isinstance(sr, str) or sr not in _SYNTACTIC_ROLES:
                    errors.append(f"{aloc}.syntactic_role: nilai tidak dikenal ({sr!r})")
                if "semantic_role" not in argument:
                    errors.append(f"{aloc}.semantic_role: field wajib; gunakan null jika belum dianotasi")
                sem = argument.get("semantic_role")
                if sem is not None and (
                    not isinstance(sem, str) or sem not in _SEMANTIC_ROLES
                ):
                    errors.append(f"{aloc}.semantic_role: nilai tidak dikenal ({sem!r})")
                if not isinstance(argument.get("required"), bool):
                    errors.append(f"{aloc}.required: harus berupa boolean")

                realizations = argument.get("realizations")
                if not isinstance(realizations, list) or not realizations:
                    errors.append(f"{aloc}.realizations: harus berupa array tidak kosong")
                    continue

                seen_realizations: set[tuple] = set()
                for ri, realization in enumerate(realizations):
                    rloc = f"{aloc}.realizations[{ri}]"
                    if not isinstance(realization, dict):
                        errors.append(f"{rloc}: realisasi harus berupa objek")
                        continue
                    errors.extend(_unknown_fields(realization, _REALIZATION_FIELDS, rloc))
                    rtype = realization.get("type")
                    if not isinstance(rtype, str) or rtype not in _REALIZATION_TYPES:
                        errors.append(f"{rloc}.type: nilai tidak dikenal ({rtype!r})")

                    preps = realization.get("prepositions")
                    if "prepositions" in realization:
                        if rtype != "PP":
                            errors.append(f"{rloc}.prepositions: hanya boleh digunakan pada realisasi PP")
                        if not isinstance(preps, list) or not preps:
                            errors.append(f"{rloc}.prepositions: harus berupa array teks tidak kosong")
                        else:
                            seen_preps: set[str] = set()
                            for pi, prep in enumerate(preps):
                                ploc = f"{rloc}.prepositions[{pi}]"
                                if not _text(prep):
                                    errors.append(f"{ploc}: harus berupa teks nonkosong")
                                    continue
                                key = prep.strip().casefold()
                                if key in seen_preps:
                                    errors.append(f"{ploc}: preposisi duplikat")
                                seen_preps.add(key)

                    if isinstance(rtype, str) and rtype in _REALIZATION_TYPES:
                        prep_key = (
                            tuple(p.strip().casefold() for p in preps)
                            if isinstance(preps, list) and all(_text(p) for p in preps)
                            else ()
                        )
                        signature = (rtype, prep_key)
                        if signature in seen_realizations:
                            errors.append(f"{rloc}: realisasi duplikat")
                        seen_realizations.add(signature)
    return errors


def validate_entries_valency(entries: Iterable[dict]) -> list[str]:
    errors: list[str] = []
    for index, entry in enumerate(entries, start=1):
        if not isinstance(entry, dict):
            errors.append(f"entri[{index}]: harus berupa objek")
            continue
        errors.extend(validate_entry_valency(entry, str(entry.get("id", f"entri[{index}]"))))
    return errors


def validate_valency_batch(path: str | Path) -> tuple[int, list[str]]:
    entries = load_batch(path)
    return len(entries), validate_entries_valency(entries)


def validate_valency_batches(paths: Iterable[str | Path]) -> list[tuple[Path, int, list[str]]]:
    results = []
    for value in paths:
        path = Path(value)
        count, errors = validate_valency_batch(path)
        results.append((path, count, errors))
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="Validasi metadata valensi per-sense.")
    parser.add_argument("batches", type=Path, nargs="+", help="Batch JSONL yang diperiksa berurutan.")
    args = parser.parse_args()
    failed = False
    total = 0
    for path in args.batches:
        print(f"\\n[{path}]")
        try:
            count, errors = validate_valency_batch(path)
        except (OSError, ValueError) as exc:
            print(f"VALIDASI VALENSI GAGAL: {exc}")
            failed = True
            continue
        total += count
        if errors:
            print("VALIDASI VALENSI GAGAL")
            for error in errors:
                print(f"- {error}")
            failed = True
        else:
            print("VALIDASI VALENSI BERHASIL")
            print(f"Entri diperiksa : {count}")
    print("\\nRINGKASAN VALIDASI VALENSI")
    print(f"Batch diperiksa : {len(args.batches)}")
    print(f"Total entri     : {total}")
    print("Catatan         : pemeriksaan struktur, bukan validasi makna anotasi.")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())

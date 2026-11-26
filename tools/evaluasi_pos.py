"""Evaluasi POS pada development split saja.

Jalankan dari root repository:
    python -m tools.evaluasi_pos
"""
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from tools.analisis_teks import analyze_text
from tools.kamus_loader import load_dictionary_directory
from tools.pencocokan_kamus import build_lexicon
from tools.pos_context import disambiguate_pos_context
from tools.pos_tagger import tag_pos

DEFAULT_DATASET = Path("data/dataset_pos/kalimat_pos_v1.jsonl")
DEFAULT_DICTIONARY = Path("data/kamus")


def load_development_records(path: str | Path = DEFAULT_DATASET) -> list[dict[str, Any]]:
    """Load only development records; reject malformed JSONL."""
    records = []
    with Path(path).open("r", encoding="utf-8") as source:
        for line_number, raw_line in enumerate(source, start=1):
            if not raw_line.strip():
                raise ValueError(f"Baris kosong pada dataset: {line_number}")
            try:
                record = json.loads(raw_line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"JSON tidak valid pada baris {line_number}: {exc.msg}") from exc
            if not isinstance(record, dict):
                raise ValueError(f"Record pada baris {line_number} harus berupa objek")
            if record.get("split") == "test":
                continue
            if record.get("split") != "development":
                raise ValueError(f"Split tidak dikenal pada baris {line_number}")
            records.append(record)
    if not records:
        raise ValueError("Dataset tidak memiliki record development")
    return records


def _score(gold_labels: list[str], predictions: list[str | None]) -> dict[str, Any]:
    """Score resolved tokens; abstentions count as uncovered and incorrect overall."""
    if len(gold_labels) != len(predictions):
        raise ValueError("Jumlah gold label dan prediksi harus sama")
    total = len(gold_labels)
    predicted = sum(value is not None for value in predictions)
    correct = sum(gold == pred for gold, pred in zip(gold_labels, predictions))
    matrix: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for gold, pred in zip(gold_labels, predictions):
        matrix[gold][pred if pred is not None else "NO_PREDICTION"] += 1
    return {
        "total": total,
        "predicted": predicted,
        "correct": correct,
        "coverage": predicted / total if total else 0.0,
        "accuracy": correct / total if total else 0.0,
        "selective_accuracy": correct / predicted if predicted else 0.0,
        "confusion": {gold: dict(counts) for gold, counts in sorted(matrix.items())},
    }


def evaluate_records(records: list[dict[str, Any]], lexicon: dict) -> dict[str, Any]:
    """Compare lexical and contextual POS decisions against development gold labels."""
    if any(record.get("split") != "development" for record in records):
        raise ValueError("Evaluator hanya menerima record split development")

    gold: list[str] = []
    lexical_predictions: list[str | None] = []
    contextual_predictions: list[str | None] = []
    gold_status_counts: Counter[str] = Counter()
    ambiguous_abstained = 0
    ambiguous_forced = 0
    sentence_count = 0

    for record in records:
        analysis = analyze_text(record["text"], lexicon)
        lexical = tag_pos(analysis)
        contextual = disambiguate_pos_context(lexical)
        source_tokens = record["tokens"]
        lexical_tokens = lexical["tokens"]
        contextual_tokens = contextual["tokens"]
        if not (len(source_tokens) == len(lexical_tokens) == len(contextual_tokens)):
            raise ValueError(f"Ketidakcocokan jumlah token pada {record.get('id')}")

        sentence_count += 1
        for annotation, lexical_item, contextual_item in zip(
            source_tokens, lexical_tokens, contextual_tokens
        ):
            if annotation["token"] != lexical_item["token"]:
                raise ValueError(f"Token tidak cocok pada {record.get('id')}")
            status = annotation["gold_status"]
            gold_status_counts[status] += 1
            labels = lexical_item.get("pos", [])
            lexical_prediction = labels[0] if len(labels) == 1 else None
            contextual_prediction = contextual_item.get("context_pos")

            if status == "resolved":
                gold.append(annotation["gold_pos"])
                lexical_predictions.append(lexical_prediction)
                contextual_predictions.append(contextual_prediction)
            elif status == "ambiguous":
                ambiguous_abstained += contextual_prediction is None
                ambiguous_forced += contextual_prediction is not None

    return {
        "sentences": sentence_count,
        "gold_status_counts": dict(sorted(gold_status_counts.items())),
        "resolved": len(gold),
        "lexical": _score(gold, lexical_predictions),
        "contextual": _score(gold, contextual_predictions),
        "ambiguous": {
            "total": ambiguous_abstained + ambiguous_forced,
            "abstained": ambiguous_abstained,
            "forced": ambiguous_forced,
        },
    }


def _print_score(title: str, result: dict[str, Any]) -> None:
    print(title)
    print(f"  Token resolved : {result['total']}")
    print(f"  Diprediksi     : {result['predicted']}")
    print(f"  Benar          : {result['correct']}")
    print(f"  Coverage       : {result['coverage']:.1%}")
    print(f"  Accuracy       : {result['accuracy']:.1%}")
    print(f"  Selective acc. : {result['selective_accuracy']:.1%}")
    print("  Confusion (gold -> prediksi):")
    for gold, row in result["confusion"].items():
        print(f"    {gold}: {dict(sorted(row.items()))}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluasi POS pada development split saja.")
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--dictionary", type=Path, default=DEFAULT_DICTIONARY)
    args = parser.parse_args()

    records = load_development_records(args.dataset)
    entries = load_dictionary_directory(args.dictionary)
    lexicon = build_lexicon(entries)
    result = evaluate_records(records, lexicon)

    print("EVALUASI POS — DEVELOPMENT SET SAJA")
    print(f"Kalimat development : {result['sentences']}")
    print(f"Token berstatus     : {result['gold_status_counts']}")
    print(f"Token resolved     : {result['resolved']}")
    _print_score("POS LEKSIKAL", result["lexical"])
    _print_score("POS DENGAN KONTEKS LOKAL", result["contextual"])
    print("PENANGANAN GOLD AMBIGUOUS")
    print(f"  Total     : {result['ambiguous']['total']}")
    print(f"  Ditahan   : {result['ambiguous']['abstained']}")
    print(f"  Dipaksakan: {result['ambiguous']['forced']}")
    print("Catatan: hasil ini hanya untuk development; bukan skor test atau akurasi umum.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

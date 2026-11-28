"""Read-only JSONL loader for reviewed context-rule records."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class ContextRulesLoadError(ValueError):
    """Context rules file is missing or structurally unreadable."""


def load_context_rules(path: str | Path) -> list[dict[str, Any]]:
    """Load JSONL objects without changing their review status or contents.

    An empty file is a valid empty rule set. Detailed rule validation remains
    the responsibility of Context Evidence Generator.
    """
    file_path = Path(path)
    try:
        lines = file_path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        raise ContextRulesLoadError(
            f"file aturan konteks tidak tersedia atau bukan UTF-8: {file_path}: {exc}"
        ) from exc

    records: list[dict[str, Any]] = []
    for line_number, raw in enumerate(lines, 1):
        if not raw.strip():
            raise ContextRulesLoadError(
                f"{file_path}:{line_number}: baris kosong tidak diizinkan"
            )
        try:
            record = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ContextRulesLoadError(
                f"{file_path}:{line_number}: JSON tidak valid: {exc.msg}"
            ) from exc
        if not isinstance(record, dict):
            raise ContextRulesLoadError(
                f"{file_path}:{line_number}: setiap baris harus berupa object JSON"
            )
        records.append(record)
    return records

"""Token-to-dictionary matching for Sistem Bahasa."""
from __future__ import annotations

import unicodedata
from collections import defaultdict
from typing import Iterable


TOKEN_FIELDS = (
    ("lemma", "lemma"),
    ("variants", "variant"),
    ("derived_forms", "derived_form"),
)


class LexiconBuildError(ValueError):
    """Raised when dictionary entries cannot form a lexical lookup index."""


def normalize_lookup_key(value: str) -> str:
    """Normalize a lookup key without rewriting punctuation or word forms."""
    if not isinstance(value, str):
        raise TypeError("token harus berupa string")
    return unicodedata.normalize("NFC", value).strip().casefold()


def build_lexicon(entries: Iterable[dict]) -> dict[str, list[dict]]:
    """Index lemmas, spelling variants, and recorded derivatives.

    Each match retains the complete original entry. Multiple entries sharing
    a key are retained as separate candidates; no sense or POS is selected.
    """
    lexicon: dict[str, list[dict]] = defaultdict(list)

    for entry_number, entry in enumerate(entries, start=1):
        if not isinstance(entry, dict):
            raise LexiconBuildError(
                f"Entri ke-{entry_number} harus berupa objek/dictionary"
            )

        entry_id = entry.get("id")
        lemma = entry.get("lemma")
        if not isinstance(entry_id, str) or not isinstance(lemma, str) or not lemma.strip():
            raise LexiconBuildError(
                f"Entri ke-{entry_number} harus memiliki id dan lemma yang valid"
            )

        for field, match_type in TOKEN_FIELDS:
            values = [lemma] if field == "lemma" else entry.get(field, [])
            if not isinstance(values, list):
                raise LexiconBuildError(
                    f"Entri {entry_id}: field {field} harus berupa array"
                )

            for form in values:
                if not isinstance(form, str) or not form.strip():
                    raise LexiconBuildError(
                        f"Entri {entry_id}: bentuk token pada {field} tidak valid"
                    )
                key = normalize_lookup_key(form)
                if not key:
                    raise LexiconBuildError(
                        f"Entri {entry_id}: bentuk token pada {field} kosong"
                    )

                lexicon[key].append(
                    {
                        "entry_id": entry_id,
                        "lemma": lemma,
                        "matched_form": form,
                        "match_type": match_type,
                        "entry": entry,
                    }
                )

    return dict(lexicon)


def lookup_token(token: str, lexicon: dict[str, list[dict]]) -> list[dict]:
    """Return every candidate match for a token, or an empty list."""
    key = normalize_lookup_key(token)
    if not key:
        return []
    return list(lexicon.get(key, []))

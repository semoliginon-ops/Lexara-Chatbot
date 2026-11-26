"""Normalisasi teks awal untuk prototipe Sistem Bahasa.

Kebijakan versi awal:
- Unicode dinormalisasi ke NFC.
- Huruf diubah menjadi lowercase.
- Rangkaian whitespace diringkas menjadi satu spasi.
- Spasi di awal/akhir dihapus.
- Tanda baca, tanda hubung, apostrof, dan kata informal dipertahankan.
"""
from __future__ import annotations

import re
import unicodedata


_WHITESPACE_RE = re.compile(r"\s+")


def normalize_text(text: str) -> str:
    """Normalize casing, Unicode composition, and whitespace.

    This function intentionally does not remove punctuation, rewrite slang,
    stem words, or alter hyphenated/apostrophized forms.
    """
    if not isinstance(text, str):
        raise TypeError("text harus berupa string")

    normalized = unicodedata.normalize("NFC", text)
    normalized = normalized.casefold()
    normalized = _WHITESPACE_RE.sub(" ", normalized)
    return normalized.strip()


if __name__ == "__main__":
    examples = (
        "  AKU   MAU makan  ",
        "GAK MAU!!!",
        "makan-makan",
        "ku'u",
        "terima kasih",
    )
    for example in examples:
        print(f"{example!r} -> {normalize_text(example)!r}")

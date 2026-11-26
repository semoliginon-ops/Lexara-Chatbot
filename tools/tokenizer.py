"""Tokenizer awal untuk prototipe Sistem Bahasa.

Kebijakan versi awal:
- Masukan dinormalisasi melalui tools.normalisasi.normalize_text.
- Rangkaian huruf/angka menjadi satu token.
- Tanda hubung dan apostrof di dalam kata dipertahankan.
- Tanda baca di luar kata menjadi token tersendiri.
- Setiap karakter tanda baca menjadi token tersendiri.
- Whitespace hanya menjadi pemisah dan tidak menghasilkan token.
"""
from __future__ import annotations

import re

from tools.normalisasi import normalize_text


_TOKEN_RE = re.compile(r"(?:[^\W_]+(?:[-'’][^\W_]+)*)|[^\w\s]", re.UNICODE)


def tokenize(text: str) -> list[str]:
    """Normalize and split text into word and punctuation tokens.

    Hyphens and apostrophes are retained when they occur between
    alphanumeric word segments. Punctuation is emitted one character
    per token. Empty or whitespace-only input returns an empty list.
    """
    normalized = normalize_text(text)
    return _TOKEN_RE.findall(normalized)


if __name__ == "__main__":
    examples = (
        "Aku mau makan nasi!",
        "Gue mager banget...",
        "Anak-anak itu bilang, 'aku gak tahu.'",
        "Harga 3.500 rupiah.",
        "makan-makan dan ku'u",
    )
    for example in examples:
        print(f"{example!r} -> {tokenize(example)!r}")

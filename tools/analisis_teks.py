"""Integrasi normalisasi, tokenisasi, dan pencocokan leksikal."""
from __future__ import annotations

import re
from typing import Any

from tools.normalisasi import normalize_text
from tools.morfologi import analyze_morphology
from tools.pencocokan_kamus import lookup_token
from tools.tokenizer import tokenize


_WORD_TOKEN_RE = re.compile(r"^[^\W_]+(?:[-'’][^\W_]+)*$", re.UNICODE)


def analyze_text(text: str, lexicon: dict[str, list[dict]]) -> dict[str, Any]:
    """Analyze text tokens against a prebuilt lexical index.

    Build the index once with build_lexicon(entries), then reuse it for
    multiple inputs. Punctuation is retained but is not looked up as a word.
    All lexical candidates are returned; this function does not choose a
    part of speech or sense.
    """
    if not isinstance(text, str):
        raise TypeError("text harus berupa string")
    if not isinstance(lexicon, dict):
        raise TypeError("lexicon harus berupa dictionary hasil build_lexicon")

    normalized = normalize_text(text)
    token_results: list[dict[str, Any]] = []

    for token in tokenize(text):
        if not _WORD_TOKEN_RE.fullmatch(token):
            token_results.append({
                "token": token,
                "kind": "punctuation",
                "status": "not_applicable",
                "candidates": [],
            })
            continue

        candidates = lookup_token(token, lexicon)
        morphology_candidates = analyze_morphology(token, lexicon)
        token_results.append({
            "token": token,
            "kind": "word",
            "status": "matched" if candidates else "unknown",
            "candidates": candidates,
            "morphology_candidates": morphology_candidates,
        })

    return {
        "normalized_text": normalized,
        "tokens": token_results,
    }

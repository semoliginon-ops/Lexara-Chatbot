"""Small, explicit POS fallback for audited high-confidence function words.

This is intentionally separate from the 3,000-entry dictionary. Additions must
be supported by development examples and regression tests; ambiguous words are
left out rather than guessed.
"""

SUPPLEMENTARY_POS = {
    # Numerals
    "dua": "NUM",
    "tiga": "NUM",
    # Prepositions
    "di": "PREP",
    "ke": "PREP",
    "pada": "PREP",
    # Coordinating/subordinating conjunctions
    "atau": "CONJ",
    "kalau": "CONJ",
    "tetapi": "CONJ",
    # Project v1 convention: aspect/modal markers and degree adverbs
    "akan": "ADV",
    "sedang": "ADV",
    "sangat": "ADV",
    "sekali": "ADV",
}


def supplementary_pos(token: str) -> str | None:
    """Return a POS only for an explicitly curated exact token."""
    if not isinstance(token, str):
        raise TypeError("token harus berupa string")
    return SUPPLEMENTARY_POS.get(token.casefold())

"""Analisis morfologi konservatif berbasis kandidat dan validasi kamus.

Modul ini tidak melakukan stemming paksa. Bentuk dasar hanya dilaporkan jika
hasil analisis dapat ditemukan di indeks leksikal yang sudah dibangun.
"""
from __future__ import annotations

from typing import Any

from tools.pencocokan_kamus import lookup_token, normalize_lookup_key


# Pola diurutkan dari prefiks terpanjang agar bentuk khusus dicoba lebih dulu.
_PREFIXES = (
    ("menge", "prefix_meN"),
    ("meny", "prefix_meN"),
    ("meng", "prefix_meN"),
    ("men", "prefix_meN"),
    ("mem", "prefix_meN"),
    ("penge", "prefix_peN"),
    ("peny", "prefix_peN"),
    ("peng", "prefix_peN"),
    ("pem", "prefix_peN"),
    ("pen", "prefix_peN"),
    ("ber", "prefix_ber"),
    ("ter", "prefix_ter"),
    ("per", "prefix_per"),
    ("di", "prefix_di"),
    ("ke", "prefix_ke"),
    ("se", "prefix_se"),
    ("me", "prefix_meN"),
)

_SUFFIXES = (
    ("kan", "suffix_kan"),
    ("an", "suffix_an"),
    ("i", "suffix_i"),
)

_NASAL_RESTORATIONS = (
    ("meng", "k"),
    ("meny", "s"),
    ("men", "t"),
    ("mem", "p"),
    ("peng", "k"),
    ("peny", "s"),
    ("pen", "t"),
    ("pem", "p"),
)


def _known_candidates(form: str, lexicon: dict[str, list[dict]]) -> list[dict]:
    return lookup_token(form, lexicon)


def analyze_morphology(
    token: str, lexicon: dict[str, list[dict]]
) -> list[dict[str, Any]]:
    """Return dictionary-validated base-word candidates for one token.

    Exact lexical matches are not re-stemmed. Unknown forms are tested against
    selected affix, confix, nasal-restoration, and reduplication patterns.
    Every returned base must exist in the supplied dictionary index.
    """
    if not isinstance(token, str):
        raise TypeError("token harus berupa string")
    if not isinstance(lexicon, dict):
        raise TypeError("lexicon harus berupa dictionary hasil build_lexicon")

    surface = normalize_lookup_key(token)
    if not surface:
        return []

    if _known_candidates(surface, lexicon):
        return []

    found: dict[tuple[str, str], dict[str, Any]] = {}

    def add_candidate(base: str, rule: str) -> None:
        base = normalize_lookup_key(base)
        if not base or base == surface:
            return
        matches = _known_candidates(base, lexicon)
        if not matches:
            return
        found[(base, rule)] = {
            "surface": surface,
            "base_form": base,
            "rule": rule,
            "candidates": matches,
        }

    # Reduplikasi penuh identik: anak-anak -> anak.
    if "-" in surface:
        left, right = surface.split("-", 1)
        if left and left == right:
            add_candidate(left, "reduplication_identical")

    # Konfiks yang cukup jelas: ke-an, per-an, serta peN-an.
    # Kandidat tetap harus lolos pencarian lema kamus.
    if surface.startswith("ke") and surface.endswith("an") and len(surface) > 5:
        add_candidate(surface[2:-2], "confix_ke_an")

    if surface.startswith("per") and surface.endswith("an") and len(surface) > 6:
        add_candidate(surface[3:-2], "confix_per_an")

    for prefix, rule in (
        ("peng", "confix_peN_an"),
        ("peny", "confix_peN_an"),
        ("pen", "confix_peN_an"),
        ("pem", "confix_peN_an"),
        ("penge", "confix_peN_an"),
    ):
        if surface.startswith(prefix) and surface.endswith("an") and len(surface) > len(prefix) + 2:
            stem = surface[len(prefix):-2]
            add_candidate(stem, rule)
            restoration = {
                "peng": "k", "peny": "s", "pen": "t", "pem": "p"
            }.get(prefix)
            if restoration:
                add_candidate(restoration + stem, rule + "_nasal_restoration")

    # Sufiks tunggal.
    for suffix, rule in _SUFFIXES:
        if surface.endswith(suffix) and len(surface) > len(suffix) + 1:
            add_candidate(surface[:-len(suffix)], rule)

    # Prefiks tunggal.
    for prefix, rule in _PREFIXES:
        if surface.startswith(prefix) and len(surface) > len(prefix) + 1:
            add_candidate(surface[len(prefix):], rule)

    # Pemulihan konsonan pada prefiks meN-/peN-.
    for prefix, restored in _NASAL_RESTORATIONS:
        if surface.startswith(prefix) and len(surface) > len(prefix):
            add_candidate(restored + surface[len(prefix):],
                          f"nasal_restoration_{prefix}")

    # Kombinasi prefiks + sufiks, misalnya mengajarkan -> ajar.
    for suffix, suffix_rule in _SUFFIXES:
        if not surface.endswith(suffix):
            continue
        middle = surface[:-len(suffix)]
        for prefix, prefix_rule in _PREFIXES:
            if middle.startswith(prefix) and len(middle) > len(prefix) + 1:
                add_candidate(middle[len(prefix):],
                              f"{prefix_rule}+{suffix_rule}")
        for prefix, restored in _NASAL_RESTORATIONS:
            if middle.startswith(prefix) and len(middle) > len(prefix):
                add_candidate(restored + middle[len(prefix):],
                              f"nasal_restoration_{prefix}+{suffix_rule}")

    return list(found.values())

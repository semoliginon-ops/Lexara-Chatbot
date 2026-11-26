"""Analisis morfologi konservatif berbasis kandidat dan validasi kamus.

Modul ini tidak melakukan stemming paksa. Bentuk dasar hanya dilaporkan jika
hasil analisis dapat ditemukan di indeks leksikal yang sudah dibangun.
"""
from __future__ import annotations

from typing import Any

from tools.pencocokan_kamus import lookup_token, normalize_lookup_key


# Aturan awal yang sengaja dibatasi. Urutan adalah urutan percobaan, bukan
# klaim bahwa semua bentuk permukaan selalu berasal dari satu pola saja.
_PREFIXES = (
    ("ber", "prefix_ber"),
    ("ter", "prefix_ter"),
    ("di", "prefix_di"),
    ("ke", "prefix_ke"),
    ("se", "prefix_se"),
    ("pe", "prefix_peN"),
    ("peng", "prefix_peN"),
    ("peny", "prefix_peN"),
    ("pen", "prefix_peN"),
    ("pem", "prefix_peN"),
    ("penge", "prefix_peN"),
    ("me", "prefix_meN"),
    ("meng", "prefix_meN"),
    ("meny", "prefix_meN"),
    ("men", "prefix_meN"),
    ("mem", "prefix_meN"),
    ("per", "prefix_per"),
)

_SUFFIXES = (
    ("kan", "suffix_kan"),
    ("i", "suffix_i"),
    ("an", "suffix_an"),
)

# Alternasi nasal yang umum pada prefiks meN-/peN-. Hanya menjadi kandidat;
# tidak pernah diterima tanpa kecocokan kamus.
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

    Exact lexical matches are not re-stemmed. For an unknown surface form,
    try a small set of affix and identical-reduplication patterns. Every
    returned candidate includes its dictionary entries and applied rules.
    """
    if not isinstance(token, str):
        raise TypeError("token harus berupa string")
    if not isinstance(lexicon, dict):
        raise TypeError("lexicon harus berupa dictionary hasil build_lexicon")

    surface = normalize_lookup_key(token)
    if not surface:
        return []

    exact = _known_candidates(surface, lexicon)
    if exact:
        return []

    found: dict[tuple[str, str], dict[str, Any]] = {}

    def add_candidate(base: str, rule: str) -> None:
        base = normalize_lookup_key(base)
        if not base or base == surface:
            return
        matches = _known_candidates(base, lexicon)
        if not matches:
            return
        key = (base, rule)
        found[key] = {
            "surface": surface,
            "base_form": base,
            "rule": rule,
            "candidates": matches,
        }

    # Reduplikasi penuh bertanda hubung: anak-anak -> anak.
    if "-" in surface:
        left, right = surface.split("-", 1)
        if left and left == right:
            add_candidate(left, "reduplication_identical")

    # Akhiran sederhana, misalnya makanan -> makan.
    for suffix, rule in _SUFFIXES:
        if surface.endswith(suffix) and len(surface) > len(suffix) + 1:
            add_candidate(surface[:-len(suffix)], rule)

    # Prefiks sederhana dan alternatif pemulihan konsonan nasal.
    for prefix, rule in _PREFIXES:
        if surface.startswith(prefix) and len(surface) > len(prefix) + 1:
            stem = surface[len(prefix):]
            add_candidate(stem, rule)

    for prefix, restored in _NASAL_RESTORATIONS:
        if surface.startswith(prefix) and len(surface) > len(prefix):
            stem = surface[len(prefix):]
            add_candidate(restored + stem, f"nasal_restoration_{prefix}")

    # Kombinasi prefiks + akhiran yang lazim, misalnya mengajarkan -> ajar.
    for suffix, suffix_rule in _SUFFIXES:
        if not surface.endswith(suffix):
            continue
        without_suffix = surface[:-len(suffix)]
        for prefix, prefix_rule in _PREFIXES:
            if without_suffix.startswith(prefix) and len(without_suffix) > len(prefix) + 1:
                stem = without_suffix[len(prefix):]
                add_candidate(stem, f"{prefix_rule}+{suffix_rule}")
        for prefix, restored in _NASAL_RESTORATIONS:
            if without_suffix.startswith(prefix) and len(without_suffix) > len(prefix):
                stem = without_suffix[len(prefix):]
                add_candidate(restored + stem, f"nasal_restoration_{prefix}+{suffix_rule}")

    return list(found.values())

"""Analisis morfologi konservatif berbasis kandidat dan validasi kamus."""
from __future__ import annotations

from typing import Any

from tools.pencocokan_kamus import lookup_token, normalize_lookup_key


_PREFIXES = (
    ("memper", "prefix_memper"),
    ("menge", "prefix_meN"), ("meny", "prefix_meN"),
    ("meng", "prefix_meN"), ("men", "prefix_meN"),
    ("mem", "prefix_meN"), ("penge", "prefix_peN"),
    ("peny", "prefix_peN"), ("peng", "prefix_peN"),
    ("pem", "prefix_peN"), ("pen", "prefix_peN"),
    ("ber", "prefix_ber"), ("ter", "prefix_ter"),
    ("per", "prefix_per"), ("di", "prefix_di"),
    ("ke", "prefix_ke"), ("se", "prefix_se"),
    ("me", "prefix_meN"),
)
_SUFFIXES = (("kan", "suffix_kan"), ("an", "suffix_an"), ("i", "suffix_i"))
_NASAL_RESTORATIONS = (
    ("meng", "k"), ("meny", "s"), ("men", "t"), ("mem", "p"),
    ("peng", "k"), ("peny", "s"), ("pen", "t"), ("pem", "p"),
)

# Bentuk leksikal yang kebetulan diawali rangkaian huruf mirip prefiks.
# Jangan analisis sebagai imbuhan jika bentuk utuh ini belum menjadi lema kamus.
_LEXICALIZED_GUARDS = {"beranda", "kemari", "kemarin", "terima", "terus", "perlu", "pernah", "terong", "selalu", "melati", "kelapa", "perang", "terapi", "mereka"}


def analyze_morphology(token: str, lexicon: dict[str, list[dict]]) -> list[dict[str, Any]]:
    """Return only dictionary-validated candidates from selected morphology rules."""
    if not isinstance(token, str):
        raise TypeError("token harus berupa string")
    if not isinstance(lexicon, dict):
        raise TypeError("lexicon harus berupa dictionary hasil build_lexicon")

    surface = normalize_lookup_key(token)
    if not surface:
        return []
    known_surface = _known(surface, lexicon)
    # A recorded derived form may also be analyzed morphologically. Exact
    # lemmas and spelling variants remain protected from accidental stemming.
    if known_surface and any(item.get("match_type") != "derived_form" for item in known_surface):
        return []
    if surface in _LEXICALIZED_GUARDS:
        return []

    # Recorded derived forms are authoritative evidence of the lemma link.
    # Prefer them over speculative segmentations (e.g. membeli -> bel/beli).
    recorded = [item for item in known_surface if item.get("match_type") == "derived_form"]
    if recorded:
        recorded_rule = None
        for prefix, rule in _PREFIXES:
            if surface.startswith(prefix):
                recorded_rule = rule
                break
        if recorded_rule:
            grouped: dict[str, list[dict[str, Any]]] = {}
            for match in recorded:
                lemma = match.get("lemma")
                if isinstance(lemma, str) and lemma:
                    grouped.setdefault(lemma, []).append(match)
            if grouped:
                return [
                    {
                        "surface": surface,
                        "base_form": lemma,
                        "rule": recorded_rule,
                        "candidates": matches,
                        "recorded_derived_form": True,
                    }
                    for lemma, matches in grouped.items()
                ]

    found: dict[tuple[str, str], dict[str, Any]] = {}

    def add_candidate(base: str, rule: str) -> None:
        base = normalize_lookup_key(base)
        if not base or base == surface:
            return
        matches = _known(base, lexicon)
        if matches:
            found[(base, rule)] = {
                "surface": surface, "base_form": base,
                "rule": rule, "candidates": matches,
            }

    if "-" in surface:
        left, right = surface.split("-", 1)
        if left and left == right:
            add_candidate(left, "reduplication_identical")
        # Reduplikasi dengan prefiks ber- pada unsur pertama,
        # misalnya berjalan-jalan atau berlari-lari.
        elif left.startswith("ber") and left[3:] == right:
            add_candidate(right, "reduplication_prefix_ber")

    if surface.startswith("ke") and surface.endswith("an") and len(surface) > 5:
        add_candidate(surface[2:-2], "confix_ke_an")
    if surface.startswith("per") and surface.endswith("an") and len(surface) > 6:
        add_candidate(surface[3:-2], "confix_per_an")

    # Periksa bentuk terpanjang lebih dahulu agar "penge-" tidak
    # tertangkap terlalu dini sebagai "pen-" atau "peng-".
    for prefix in ("penge", "peng", "peny", "pem", "pen"):
        if surface.startswith(prefix) and surface.endswith("an") and len(surface) > len(prefix) + 2:
            stem = surface[len(prefix):-2]
            add_candidate(stem, "confix_peN_an")
            restoration = {"peng": "k", "peny": "s", "pen": "t", "pem": "p"}.get(prefix)
            # Jangan pulihkan konsonan jika bentuk tanpa restorasi sudah
            # merupakan lema. Contoh: pengajaran -> ajar, bukan kajar.
            if restoration and not _known(stem, lexicon):
                add_candidate(restoration + stem, "confix_peN_an_nasal_restoration")
            break

    # Imbuhan bertingkat di- + per- + sufiks, misalnya diperbaiki.
    # Analisis lapisan luar (di-) dahulu, lalu pola per-...-i/-kan.
    if surface.startswith("di"):
        inner = surface[2:]
        for suffix, suffix_rule in _SUFFIXES:
            # Bentuk pasif turunan memper- memakai -i atau -kan;
            # jangan menganggap konfiks nominal -an sebagai pola ini.
            if suffix not in ("i", "kan"):
                continue
            if inner.endswith(suffix) and len(inner) > len(suffix) + 3:
                middle = inner[:-len(suffix)]
                if middle.startswith("per") and len(middle) > 4:
                    add_candidate(
                        middle[3:],
                        f"prefix_di+prefix_per+{suffix_rule}",
                    )

    for suffix, rule in _SUFFIXES:
        if surface.endswith(suffix) and len(surface) > len(suffix) + 1:
            add_candidate(surface[:-len(suffix)], rule)

    for prefix, rule in _PREFIXES:
        if surface.startswith(prefix) and len(surface) > len(prefix) + 1:
            remainder = surface[len(prefix):]
            # Untuk alomorf nasal yang meluluhkan konsonan awal t/p,
            # prioritaskan hasil restorasi jika bentuk itu memang ada di kamus.
            # Bentuk seperti menyanyi tetap dapat memakai remainder "nyanyi"
            # jika kandidat restorasi s+nyanyi tidak dikenal.
            # Pada meny-/peny-, konsonan awal "ny" dapat tetap menjadi
            # bagian lema, misalnya menyanyi -> nyanyi. Prioritaskan
            # kandidat ini hanya jika lema tersebut benar-benar ada.
            retained_ny = prefix in ("meny", "peny") and _known("ny" + remainder, lexicon)
            if retained_ny:
                add_candidate("ny" + remainder, f"nasal_retention_{prefix}")
            else:
                restoration = {
                    "men": "t", "mem": "p", "pen": "t", "pem": "p",
                }.get(prefix)
                if not (restoration and _known(restoration + remainder, lexicon)):
                    add_candidate(remainder, rule)
            break

    for prefix, restored in _NASAL_RESTORATIONS:
        if surface.startswith(prefix) and len(surface) > len(prefix):
            remainder = surface[len(prefix):]
            # Untuk meng-/peng-, jangan tambahkan kandidat k+remainder
            # jika remainder sendiri sudah merupakan lema kamus.
            # Contoh: mengambil/pengambil -> ambil, bukan kambil.
            if prefix in ("meng", "peng") and _known(remainder, lexicon):
                continue
            if prefix in ("meny", "peny") and _known("ny" + remainder, lexicon):
                continue
            add_candidate(restored + remainder, f"nasal_restoration_{prefix}")

    for suffix, suffix_rule in _SUFFIXES:
        if not surface.endswith(suffix):
            continue
        middle = surface[:-len(suffix)]
        for prefix, prefix_rule in _PREFIXES:
            if middle.startswith(prefix) and len(middle) > len(prefix) + 1:
                remainder = middle[len(prefix):]
                retained_ny = prefix in ("meny", "peny") and _known("ny" + remainder, lexicon)
                if retained_ny:
                    add_candidate("ny" + remainder, f"nasal_retention_{prefix}+{suffix_rule}")
                else:
                    restoration = {
                        "men": "t", "mem": "p", "pen": "t", "pem": "p",
                    }.get(prefix)
                    if not (restoration and _known(restoration + remainder, lexicon)):
                        add_candidate(remainder, f"{prefix_rule}+{suffix_rule}")
                break
        for prefix, restored in _NASAL_RESTORATIONS:
            if middle.startswith(prefix) and len(middle) > len(prefix):
                remainder = middle[len(prefix):]
                if prefix in ("meng", "peng") and _known(remainder, lexicon):
                    continue
                if prefix in ("meny", "peny") and _known("ny" + remainder, lexicon):
                    continue
                add_candidate(restored + remainder, f"nasal_restoration_{prefix}+{suffix_rule}")

    return list(found.values())


def _known(form: str, lexicon: dict[str, list[dict]]) -> list[dict]:
    return lookup_token(form, lexicon)

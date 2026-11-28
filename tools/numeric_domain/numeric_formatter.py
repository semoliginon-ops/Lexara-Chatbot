"""Format Decimal values using Indonesian digit grouping conventions."""

from decimal import Decimal, InvalidOperation


def format_number(value: Decimal, *, decimal_places=None) -> str:
    """Format a number with dot thousands and comma decimal separators."""
    try:
        number = value if isinstance(value, Decimal) else Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError("Nilai numerik tidak valid.") from exc

    if not number.is_finite():
        raise ValueError("NaN dan infinity tidak dapat diformat.")

    if decimal_places is not None:
        if not isinstance(decimal_places, int) or decimal_places < 0:
            raise ValueError("decimal_places harus bilangan bulat nonnegatif.")
        number = number.quantize(Decimal(1).scaleb(-decimal_places))

    rendered = format(number, "f")
    if "." in rendered:
        integer, fraction = rendered.split(".", 1)
        fraction = fraction.rstrip("0")
    else:
        integer, fraction = rendered, ""

    sign = ""
    if integer.startswith("-"):
        sign, integer = "-", integer[1:]

    groups = []
    while integer:
        groups.append(integer[-3:])
        integer = integer[:-3]
    integer = ".".join(reversed(groups)) if groups else "0"

    return sign + integer + ("," + fraction if fraction else "")

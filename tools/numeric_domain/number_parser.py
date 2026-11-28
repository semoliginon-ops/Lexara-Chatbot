"""Parse numeric literals without consulting the lexical dictionary."""

from decimal import Decimal, InvalidOperation
import re


class NumericParseError(ValueError):
    """Raised when a numeric literal is malformed or unsupported."""


_DIGITS = r"\d+"
_GROUPED = rf"(?:{_DIGITS}|\d{{1,3}}(?:[., ]\d{{3}})+)"
_NUMBER_RE = re.compile(
    rf"^[+-]?(?:(?:{_GROUPED})(?:[.,]\d+)?|[.,]\d+)$"
)


def parse_number(value: str) -> Decimal:
    """Parse an Indonesian- or English-style numeric literal.

    Examples:
      1250       -> Decimal('1250')
      1.250,75   -> Decimal('1250.75')
      1,250.75   -> Decimal('1250.75')
      12,5       -> Decimal('12.5')
      -0,25      -> Decimal('-0.25')

    A trailing percent sign is accepted and converted to its ratio
    (for example, '25%' becomes Decimal('0.25')).
    """
    if not isinstance(value, str):
        raise NumericParseError("Input angka harus berupa teks.")

    text = value.strip().replace("\u00a0", " ")
    if not text:
        raise NumericParseError("Angka tidak boleh kosong.")

    is_percent = text.endswith("%")
    if is_percent:
        text = text[:-1].strip()
        if not text:
            raise NumericParseError("Nilai persentase tidak boleh kosong.")

    if not _NUMBER_RE.fullmatch(text):
        raise NumericParseError(f"Format angka tidak valid: {value!r}")

    sign = ""
    if text[0] in "+-":
        sign, text = text[0], text[1:]

    # Spaces are accepted only as three-digit grouping separators.
    text = text.replace(" ", "")

    if "." in text and "," in text:
        # The rightmost separator is the decimal separator.
        decimal_sep = "." if text.rfind(".") > text.rfind(",") else ","
        group_sep = "," if decimal_sep == "." else "."
        integer, fraction = text.rsplit(decimal_sep, 1)
        integer = integer.replace(group_sep, "")
        normalized = integer + "." + fraction
    elif "." in text or "," in text:
        separator = "." if "." in text else ","
        parts = text.split(separator)
        if len(parts) > 2:
            # Repeated separators are thousands grouping only.
            if not all(len(part) == 3 for part in parts[1:]) or not (1 <= len(parts[0]) <= 3):
                raise NumericParseError(f"Format angka tidak valid: {value!r}")
            normalized = "".join(parts)
        elif len(parts) == 2:
            left, right = parts
            if len(right) == 3 and 1 <= len(left) <= 3:
                # Indonesian convention: a single three-digit group is thousands.
                normalized = left + right
            else:
                normalized = left + "." + right
        else:
            normalized = text
    else:
        normalized = text

    try:
        number = Decimal(sign + normalized)
    except InvalidOperation as exc:
        raise NumericParseError(f"Format angka tidak valid: {value!r}") from exc

    if not number.is_finite():
        raise NumericParseError("NaN dan infinity tidak didukung.")
    return number / Decimal(100) if is_percent else number

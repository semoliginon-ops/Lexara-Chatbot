"""Standalone numeric domain for parsing numeric literals and evaluating arithmetic."""

from .calculator import calculate, percent_of
from .number_parser import NumericParseError, parse_number
from .numeric_formatter import format_number

__all__ = [
    "NumericParseError",
    "calculate",
    "format_number",
    "parse_number",
    "percent_of",
]

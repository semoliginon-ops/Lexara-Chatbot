import unittest
from decimal import Decimal

from tools.numeric_domain import calculate, format_number, parse_number, percent_of
from tools.numeric_domain.calculator import CalculationError
from tools.numeric_domain.number_parser import NumericParseError


class NumericParserTests(unittest.TestCase):
    def test_integer(self):
        self.assertEqual(parse_number("1250"), Decimal("1250"))

    def test_indonesian_grouping_and_decimal(self):
        self.assertEqual(parse_number("1.250,75"), Decimal("1250.75"))

    def test_english_grouping_and_decimal(self):
        self.assertEqual(parse_number("1,250.75"), Decimal("1250.75"))

    def test_decimal_comma(self):
        self.assertEqual(parse_number("12,5"), Decimal("12.5"))

    def test_single_three_digit_group_is_thousands(self):
        self.assertEqual(parse_number("1.250"), Decimal("1250"))
        self.assertEqual(parse_number("1,250"), Decimal("1250"))

    def test_sign_and_whitespace_grouping(self):
        self.assertEqual(parse_number("-1 250"), Decimal("-1250"))

    def test_percent_is_ratio(self):
        self.assertEqual(parse_number("25%"), Decimal("0.25"))

    def test_rejects_malformed_values(self):
        for value in ("", "12,34,56", "1..2", "abc", "NaN", "Infinity", "1,2,3"):
            with self.subTest(value=value), self.assertRaises(NumericParseError):
                parse_number(value)


class CalculatorTests(unittest.TestCase):
    def test_basic_operations(self):
        self.assertEqual(calculate("10 + 5 - 2"), Decimal("13"))
        self.assertEqual(calculate("6 * 7"), Decimal("42"))
        self.assertEqual(calculate("20 / 4"), Decimal("5"))

    def test_operator_precedence(self):
        self.assertEqual(calculate("2 + 3 * 4"), Decimal("14"))

    def test_parentheses(self):
        self.assertEqual(calculate("(2 + 3) * 4"), Decimal("20"))

    def test_unary_negative(self):
        self.assertEqual(calculate("-5 + 2"), Decimal("-3"))

    def test_decimal_arithmetic_is_exact(self):
        self.assertEqual(calculate("0,1 + 0,2"), Decimal("0.3"))

    def test_percent_literal(self):
        self.assertEqual(calculate("200 * 25%"), Decimal("50.00"))

    def test_power(self):
        self.assertEqual(calculate("2 ** 10"), Decimal("1024"))

    def test_percent_of(self):
        self.assertEqual(percent_of("20", "150000"), Decimal("30000"))

    def test_division_by_zero(self):
        with self.assertRaises(CalculationError):
            calculate("10 / 0")

    def test_rejects_incomplete_or_unsafe_expressions(self):
        for expression in ("", "2 +", "__import__('os')", "1 // 2", "2 ** 10001"):
            with self.subTest(expression=expression), self.assertRaises(CalculationError):
                calculate(expression)


class NumericFormatterTests(unittest.TestCase):
    def test_indonesian_format(self):
        self.assertEqual(format_number(Decimal("1234567.8900")), "1.234.567,89")

    def test_negative_format(self):
        self.assertEqual(format_number(Decimal("-1234.5")), "-1.234,5")

    def test_fixed_decimal_places(self):
        self.assertEqual(format_number(Decimal("12.345"), decimal_places=2), "12,34")


if __name__ == "__main__":
    unittest.main()

"""Deterministic Decimal-based arithmetic expression evaluator."""

from decimal import Decimal, DivisionByZero, InvalidOperation, localcontext
import re

from .number_parser import NumericParseError, parse_number


class CalculationError(ValueError):
    """Raised when an arithmetic expression cannot be evaluated."""


_TOKEN_RE = re.compile(
    r"\s*(?:(\d+(?:[.,]\d+)?(?:%?)|[.,]\d+(?:%)?)|([()+*/-]|\*\*))"
)


class _Parser:
    def __init__(self, expression: str):
        if not isinstance(expression, str) or not expression.strip():
            raise CalculationError("Ekspresi perhitungan tidak boleh kosong.")
        self.tokens = self._tokenize(expression)
        self.position = 0

    @staticmethod
    def _tokenize(expression: str):
        tokens = []
        position = 0
        while position < len(expression):
            match = _TOKEN_RE.match(expression, position)
            if not match:
                if expression[position:].strip() == "":
                    break
                raise CalculationError(
                    f"Karakter atau format tidak didukung di posisi {position}."
                )
            number, operator = match.groups()
            tokens.append(number if number is not None else operator)
            position = match.end()
        if not tokens:
            raise CalculationError("Tidak ada angka untuk dihitung.")
        return tokens

    def _peek(self):
        return self.tokens[self.position] if self.position < len(self.tokens) else None

    def _take(self, expected=None):
        token = self._peek()
        if token is None or (expected is not None and token != expected):
            raise CalculationError(f"Ekspresi tidak lengkap; diharapkan {expected or 'nilai'}.")
        self.position += 1
        return token

    def parse(self):
        result = self._expression()
        if self._peek() is not None:
            raise CalculationError(f"Token berlebih: {self._peek()!r}.")
        return result

    def _expression(self):
        value = self._term()
        while self._peek() in ("+", "-"):
            operator = self._take()
            right = self._term()
            value = value + right if operator == "+" else value - right
        return value

    def _term(self):
        value = self._unary()
        while self._peek() in ("*", "/"):
            operator = self._take()
            right = self._unary()
            if operator == "*":
                value *= right
            else:
                if right == 0:
                    raise CalculationError("Tidak bisa membagi dengan nol.")
                value /= right
        return value

    def _unary(self):
        if self._peek() == "+":
            self._take("+")
            return self._unary()
        if self._peek() == "-":
            self._take("-")
            return -self._unary()
        return self._power()

    def _power(self):
        value = self._primary()
        if self._peek() == "**":
            self._take("**")
            exponent = self._unary()
            if exponent != exponent.to_integral_value() or abs(exponent) > 10000:
                raise CalculationError("Pangkat harus bilangan bulat dengan nilai paling besar 10.000.")
            if value == 0 and exponent < 0:
                raise CalculationError("Nol tidak dapat dipangkatkan dengan bilangan negatif.")
            value = value ** int(exponent)
        return value

    def _primary(self):
        token = self._peek()
        if token == "(":
            self._take("(")
            value = self._expression()
            self._take(")")
            return value
        if token is None:
            raise CalculationError("Nilai angka tidak ditemukan.")
        if token in (")", "*", "/", "**"):
            raise CalculationError(f"Token {token!r} tidak dapat digunakan sebagai angka.")
        self._take()
        try:
            return parse_number(token)
        except NumericParseError as exc:
            raise CalculationError(str(exc)) from exc


def calculate(expression: str) -> Decimal:
    """Evaluate +, -, *, /, **, parentheses, and percent literals.

    Percent literals are ratios: 25% is 0.25, so 200 * 25% is 50.
    Use percent_of(25, 200) for the explicit phrase '25 percent of 200'.
    """
    try:
        with localcontext() as context:
            context.prec = 28
            result = _Parser(expression).parse()
            if not result.is_finite():
                raise CalculationError("Hasil perhitungan tidak terhingga.")
            return +result
    except (DivisionByZero, InvalidOperation, OverflowError, ZeroDivisionError) as exc:
        raise CalculationError("Perhitungan tidak dapat diselesaikan.") from exc


def percent_of(percent, base) -> Decimal:
    """Return a percentage of a base value."""
    try:
        rate = percent if isinstance(percent, Decimal) else parse_number(str(percent))
        amount = base if isinstance(base, Decimal) else parse_number(str(base))
        with localcontext() as context:
            context.prec = 28
            return +(rate * amount / Decimal(100))
    except (NumericParseError, InvalidOperation, OverflowError) as exc:
        raise CalculationError("Nilai persentase atau nilai dasar tidak valid.") from exc

"""Public API: multiply two hypercomplex expression strings."""
from .fast_resolver import FastResolver
from .formatter import ExpressionFormatter
from .parser import ExpressionParser
from .resolver import BasisProductResolver
from .sparse import SparseMultiplier


class ExpressionMultiplier:
    """Composes parser -> sparse multiplier -> formatter."""

    def __init__(self, resolver: BasisProductResolver | None = None):
        resolver = resolver or FastResolver()
        self._parser = ExpressionParser()
        self._formatter = ExpressionFormatter()
        self._multiplier = SparseMultiplier(resolver)

    def multiply(self, expr_a: str, expr_b: str) -> str:
        a = self._parser.parse(expr_a)
        b = self._parser.parse(expr_b)
        return self._formatter.format(self._multiplier.multiply(a, b))


_default: ExpressionMultiplier | None = None


def multiply_expressions(expr_a: str, expr_b: str) -> str:
    """Module-level convenience function."""
    global _default
    if _default is None:
        _default = ExpressionMultiplier()
    return _default.multiply(expr_a, expr_b)
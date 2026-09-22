"""Public API: multiply two hypercomplex expression strings."""
from .adapters import create_resolver
from .core import BasisProductResolver, SparseMultiplier
from .expression import ExpressionParser, ExpressionFormatter


class ExpressionMultiplier:
    """Multiplies two hypercomplex expression strings.

    Composes: parser -> sparse multiplier -> formatter.
    The algebra kind (and dim, for split) is fixed at construction, which
    keeps standard/split — and different split dims — from ever mixing.
    """

    def __init__(
        self,
        kind: str = "standard",
        dim: int | None = None,
        resolver: BasisProductResolver | None = None,
    ):
        self._resolver = resolver if resolver is not None else create_resolver(kind, dim)
        self._kind = kind
        self._parser = ExpressionParser()
        self._formatter = ExpressionFormatter()
        self._multiplier = SparseMultiplier(self._resolver)

    @property
    def kind(self) -> str:
        return self._kind

    def multiply(self, expr_a: str, expr_b: str) -> str:
        a = self._parser.parse(expr_a)
        b = self._parser.parse(expr_b)
        product = self._multiplier.multiply(a, b)
        return self._formatter.format(product)


# --- module-level convenience functions ----------------------------------

_standard_multiplier: ExpressionMultiplier | None = None
_split_multipliers: dict[int, ExpressionMultiplier] = {}


def multiply_expressions(expr_a: str, expr_b: str) -> str:
    """Multiply two expressions in the standard algebra."""
    global _standard_multiplier
    if _standard_multiplier is None:
        _standard_multiplier = ExpressionMultiplier(kind="standard")
    return _standard_multiplier.multiply(expr_a, expr_b)


def multiply_split_expressions(expr_a: str, expr_b: str, dim: int) -> str:
    """Multiply two expressions in a split algebra of the given dim.

    A separate multiplier is cached per dim. Mixing split dimensions is not
    allowed — each dim is its own algebra and gets its own multiplier.
    """
    if dim not in _split_multipliers:
        _split_multipliers[dim] = ExpressionMultiplier(kind="split", dim=dim)
    return _split_multipliers[dim].multiply(expr_a, expr_b)
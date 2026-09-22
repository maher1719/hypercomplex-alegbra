"""Application service: multiplies hypercomplex expressions."""
import logging

from ..adapters import create_resolver
from ..core import BasisProductResolver, SparseMultiplier
from ..expression import ExpressionParser, ExpressionFormatter

logger = logging.getLogger(__name__)


class ExpressionMultiplier:
    """Multiplies hypercomplex expression strings.

    The algebra kind (and dim, for split) is fixed at construction, which
    keeps standard/split — and different split dims — from ever mixing.

    Two sister operations, one pinned algebra/dim:
        multiply(a, b)        ME  — binary multiply
        multiply_many([...])  MM  — left-associative fold

    enforce_check (default True):
        True  -> validate EVERY expression upfront (syntax + algebra bounds)
                 and log the check result, even when the product becomes 0.
        False -> skip the check; use the fast lazy fold with zero
                 short-circuit (elements after a zero are not validated).
    """

    def __init__(
        self,
        kind: str = "standard",
        dim: int | None = None,
        resolver: BasisProductResolver | None = None,
        enforce_check: bool = True,
    ):
        self._resolver = resolver if resolver is not None else create_resolver(kind, dim)
        self._kind = kind
        self._enforce_check = enforce_check
        self._parser = ExpressionParser()
        self._formatter = ExpressionFormatter()
        self._multiplier = SparseMultiplier(self._resolver)

    @property
    def kind(self) -> str:
        return self._kind

    def multiply(self, expr_a: str, expr_b: str) -> str:
        """ME: multiply two expressions."""
        a = self._parser.parse(expr_a)
        b = self._parser.parse(expr_b)
        return self._formatter.format(self._multiplier.multiply(a, b))

    def multiply_many(self, expressions) -> str:
        """MM: multiply a sequence, left-associative. ((a·b)·c)·d ...

        Bracketing matters for octonions and above (non-associative), so
        this fold is strictly left-to-right. Nest multiply() for other
        bracketings.
        """
        exprs = list(expressions)
        if not exprs:
            raise ValueError("multiply_many needs at least one expression")

        if self._enforce_check:
            return self._multiply_many_checked(exprs)
        return self._multiply_many_fast(exprs)

    # -- checked path (enforce_check=True) --------------------------------
    def _multiply_many_checked(self, exprs):
        parsed_list = []
        for k, expr in enumerate(exprs):
            try:
                parsed = self._parser.parse(expr)
            except ValueError as e:
                logger.info("MM check: expr[%d] = %r failed to parse: %s", k, expr, e)
                raise
            try:
                for idx in parsed:
                    self._resolver.resolve(idx, 0)  # validate index bounds
            except ValueError as e:
                logger.info("MM check: expr[%d] = %r out of range: %s", k, expr, e)
                raise
            parsed_list.append(parsed)
        logger.info("MM check: all %d expressions valid", len(exprs))

        acc = parsed_list[0]
        for parsed in parsed_list[1:]:
            acc = self._multiplier.multiply(acc, parsed)
            if not acc:
                logger.info(
                    "MM check: product became zero; short-circuiting "
                    "(all %d expressions were validated)", len(exprs)
                )
                return "0"
        return self._formatter.format(acc)

    # -- fast path (enforce_check=False) ----------------------------------
    def _multiply_many_fast(self, exprs):
        acc = self._parser.parse(exprs[0])
        for expr in exprs[1:]:
            b = self._parser.parse(expr)
            acc = self._multiplier.multiply(acc, b)
            if not acc:
                return "0"
        return self._formatter.format(acc)
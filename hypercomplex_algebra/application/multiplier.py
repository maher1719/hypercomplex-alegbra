"""Application service: multiplies hypercomplex expressions."""
import logging

from ..adapters import create_resolver
from ..core import BasisProductResolver, SparseMultiplier, DualSparseMultiplier
from ..expression import ElementParser, ElementFormatter
from ..expression import DualElementFormatter, DualElementParser


logger = logging.getLogger(__name__)

DUAL_KINDS = ("dual", "dual_split")


class ExpressionMultiplier:
    def __init__(
        self,
        kind: str = "standard",
        dim: int | None = None,
        resolver=None,
        enforce_check: bool = True,
    ):
        self._kind = kind
        self._enforce_check = enforce_check

        # Resolver: selected by the factory based on kind (+ dim for split/dual_split)
        self._resolver = resolver if resolver is not None else create_resolver(kind, dim)

        # Parser / formatter / multiplier: picked by algebra family
        if kind in DUAL_KINDS:
            self._parser = DualElementParser() 
            self._formatter = DualElementFormatter()
            self._multiplier = DualSparseMultiplier(self._resolver)
        else:  # standard, split
            self._parser = ElementParser()
            self._formatter = ElementFormatter()
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
        
        # 1. Parse and explicitly validate EVERY expression upfront
        for k, expr in enumerate(exprs):
            try:
                parsed = self._parser.parse(expr)
            except ValueError as e:
                logger.info("MM check: expr[%d] = %r failed to parse: %s", k, expr, e)
                raise
            
            # Validate index bounds based on algebra family
            try:
                if self._kind in DUAL_KINDS:
                    for idx, eps in parsed:
                        # Dual resolver expects (i, eps_i, j, eps_j)
                        # Multiply by identity (0, 0) just to trigger the bounds check
                        self._resolver.resolve(idx, eps, 0, 0)
                else:
                    for idx in parsed:
                        self._resolver.resolve(idx, 0)
            except ValueError as e:
                logger.info("MM check: expr[%d] = %r out of range: %s", k, expr, e)
                raise
                
            parsed_list.append(parsed)
            
        logger.info("MM check: all %d expressions valid", len(exprs))

        # 2. Fold the validated expressions
        acc = parsed_list[0]
        for next_parsed in parsed_list[1:]:  # renamed to avoid any shadowing issues
            acc = self._multiplier.multiply(acc, next_parsed)
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
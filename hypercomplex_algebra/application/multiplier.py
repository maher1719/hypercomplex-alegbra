"""Application service: multiplies hypercomplex expressions."""
import logging

from ..adapters import create_resolver, create_tensor_resolver
from ..core import (
    SparseMultiplier, DualSparseMultiplier, TensorSparseMultiplier,
)
from ..expression import (
    ElementParser, ElementFormatter,
    DualElementParser, DualElementFormatter,
    TensorElementParser, TensorElementFormatter,
)

logger = logging.getLogger(__name__)

DUAL_KINDS = ("dual", "dual_split")
TENSOR_KINDS = ("tensor",)


class ExpressionMultiplier:
    def __init__(
        self,
        kind: str = "standard",
        dim: int | None = None,
        slots=None,
        resolver=None,
    ):
        self._kind = kind

        # Resolver selection
        if resolver is not None:
            self._resolver = resolver
        elif kind in TENSOR_KINDS:
            if slots is None:
                raise ValueError("slots is required for the tensor algebra")
            self._resolver = create_tensor_resolver(slots)
        else:
            self._resolver = create_resolver(kind, dim)

        # Parser / formatter / multiplier by algebra family
        if kind in TENSOR_KINDS:
            num_slots = self._resolver.num_slots
            self._parser = TensorElementParser(num_slots)
            self._formatter = TensorElementFormatter()
            self._multiplier = TensorSparseMultiplier(self._resolver)
        elif kind in DUAL_KINDS:
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

        Every expression is parsed and range-validated up front, before any
        multiplication happens — including terms that a later zero would
        otherwise short-circuit past. This is the only behavior; there is
        no faster, unchecked mode. The validation is a resolve() call per
        basis index (not a full multiplication), so the cost is small.
        """
        exprs = list(expressions)
        if not exprs:
            raise ValueError("multiply_many needs at least one expression")
        return self._multiply_many_checked(exprs)

    def _multiply_many_checked(self, exprs):
        parsed_list = []
        for k, expr in enumerate(exprs):
            try:
                parsed = self._parser.parse(expr)
            except ValueError as e:
                logger.info("MM check: expr[%d] = %r failed to parse: %s", k, expr, e)
                raise
            try:
                self._validate_parsed_element(parsed)
            except ValueError as e:
                logger.info("MM check: expr[%d] = %r out of range: %s", k, expr, e)
                raise
            parsed_list.append(parsed)

        logger.info("MM check: all %d expressions valid", len(exprs))

        acc = parsed_list[0]
        for next_parsed in parsed_list[1:]:
            acc = self._multiplier.multiply(acc, next_parsed)
            if not acc:
                logger.info(
                    "MM check: product became zero; short-circuiting "
                    "(all %d expressions were validated)", len(exprs)
                )
                return "0"
        return self._formatter.format(acc)

    def _validate_parsed_element(self, parsed):
        """Validate all basis indices against the resolver's bounds."""
        if self._kind in TENSOR_KINDS:
            identity = (0,) * self._resolver.num_slots
            for key in parsed:
                self._resolver.resolve(key, identity)
        else:
            # Let the resolver's own ValueError (with its specific message —
            # e.g. "Index out of range for split dim=3 (valid: 0..7)...")
            # propagate as-is. It used to be caught here and replaced with a
            # generic "unsupported format", which threw away the one piece
            # of information the caller actually needed.
            if self._kind in DUAL_KINDS:
                for idx, eps in parsed:
                    self._resolver.resolve(idx, eps, 0, 0)
            else:
                for idx in parsed:
                    self._resolver.resolve(idx, 0)
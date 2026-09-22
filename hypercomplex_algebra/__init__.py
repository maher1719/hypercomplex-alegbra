"""hypercomplex_algebra: sparse expression multiplication on top of hypercomplex-engine."""

from .core import BasisProductResolver, SparseMultiplier
from .adapters import StandardResolver, SplitResolver, create_resolver
from .expression import ExpressionParser, ExpressionFormatter
from .facade import (
    ExpressionMultiplier,
    multiply_expressions,
    multiply_split_expressions,
)

__all__ = [
    # core
    "BasisProductResolver",
    "SparseMultiplier",
    # adapters
    "StandardResolver",
    "SplitResolver",
    "create_resolver",
    # expression
    "ExpressionParser",
    "ExpressionFormatter",
    # facade
    "ExpressionMultiplier",
    "multiply_expressions",
    "multiply_split_expressions",
]
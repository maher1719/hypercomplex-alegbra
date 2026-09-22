"""Facade: the simplest possible entry points.

Outermost layer. Holds ready-to-use multiplier instances (cached per
algebra/dim) and exposes flat convenience functions. All real work is
delegated to the application-layer ExpressionMultiplier.
"""
from .application import ExpressionMultiplier

_standard_multiplier: ExpressionMultiplier | None = None
_split_multipliers: dict[int, ExpressionMultiplier] = {}
_dual_multiplier: ExpressionMultiplier | None = None
_dual_split_multipliers: dict[int, ExpressionMultiplier] = {}


def _get_standard_multiplier() -> ExpressionMultiplier:
    global _standard_multiplier
    if _standard_multiplier is None:
        _standard_multiplier = ExpressionMultiplier(kind="standard")
    return _standard_multiplier


def _get_split_multiplier(dim: int) -> ExpressionMultiplier:
    if dim not in _split_multipliers:
        _split_multipliers[dim] = ExpressionMultiplier(kind="split", dim=dim)
    return _split_multipliers[dim]


def _get_dual_multiplier() -> ExpressionMultiplier:
    global _dual_multiplier
    if _dual_multiplier is None:
        _dual_multiplier = ExpressionMultiplier(kind="dual")
    return _dual_multiplier

def _get_dual_split_multiplier(dim: int) -> ExpressionMultiplier:
    if dim not in _dual_split_multipliers:
        _dual_split_multipliers[dim] = ExpressionMultiplier(kind="dual_split", dim=dim)
    return _dual_split_multipliers[dim]





def multiply_expressions(expr_a: str, expr_b: str) -> str:
    """ME: multiply two expressions in the standard algebra."""
    return _get_standard_multiplier().multiply(expr_a, expr_b)


def multiply_many_expressions(expressions) -> str:
    """MM: left-fold a sequence of expressions in the standard algebra."""
    return _get_standard_multiplier().multiply_many(expressions)


def multiply_split_expressions(expr_a: str, expr_b: str, dim: int) -> str:
    """ME for a split algebra at a fixed dim."""
    return _get_split_multiplier(dim).multiply(expr_a, expr_b)


def multiply_many_split_expressions(expressions, dim: int) -> str:
    """MM for a split algebra at a fixed dim. Same dim rule as ME."""
    return _get_split_multiplier(dim).multiply_many(expressions)




def multiply_dual_expressions(expr_a: str, expr_b: str) -> str:
    """ME: multiply two expressions in the dual algebra (standard parent)."""
    return _get_dual_multiplier().multiply(expr_a, expr_b)


def multiply_many_dual_expressions(expressions) -> str:
    """MM: left-fold a sequence of expressions in the dual algebra."""
    return _get_dual_multiplier().multiply_many(expressions)


def multiply_dual_split_expressions(expr_a: str, expr_b: str, dim: int) -> str:
    """ME: multiply two expressions in a dual_split algebra at a fixed dim."""
    return _get_dual_split_multiplier(dim).multiply(expr_a, expr_b)


def multiply_many_dual_split_expressions(expressions, dim: int) -> str:
    """MM: left-fold a sequence of expressions in a dual_split algebra."""
    return _get_dual_split_multiplier(dim).multiply_many(expressions)
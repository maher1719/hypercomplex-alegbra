"""Factory for building resolvers from an algebra kind + config."""
from ..core.resolver import BasisProductResolver
from .standard_resolver import StandardResolver
from .split_resolver import SplitResolver


def create_resolver(kind: str, dim: int | None = None) -> BasisProductResolver:
    """Build the resolver for a given algebra kind.

    Args:
        kind: 'standard' or 'split' (dual/tensor coming).
        dim: required for 'split'.
    """
    kind = kind.lower().strip()
    if kind == "standard":
        return StandardResolver()
    if kind == "split":
        if dim is None:
            raise ValueError("dim is required for the split algebra")
        return SplitResolver(dim)
    raise ValueError(f"Unknown algebra kind: {kind!r}")
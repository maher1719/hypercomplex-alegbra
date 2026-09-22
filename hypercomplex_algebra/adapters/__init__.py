from ..core.resolver import BasisProductResolver
from .standard_resolver import StandardResolver
from .split_resolver import SplitResolver


def create_resolver(kind: str, dim: int | None = None) -> BasisProductResolver:
    """Factory: build the resolver for a given algebra kind.

    Args:
        kind: 'standard' or 'split'.
        dim: required for 'split' (the split doubling level).

    Returns:
        A resolver implementing the BasisProductResolver contract.
    """
    kind = kind.lower().strip()
    if kind == "standard":
        return StandardResolver()
    if kind == "split":
        if dim is None:
            raise ValueError("dim is required for the split algebra")
        return SplitResolver(dim)
    raise ValueError(f"Unknown algebra kind: {kind!r}")


__all__ = ["StandardResolver", "SplitResolver", "create_resolver"]
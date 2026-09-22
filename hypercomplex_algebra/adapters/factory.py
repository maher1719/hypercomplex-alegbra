"""Factory for building resolvers from an algebra kind + config."""
from ..core.resolver import BasisProductResolver
from .standard_resolver import StandardResolver
from .split_resolver import SplitResolver
from .dual_standard_resolver import DualStandardResolver
from .dual_split_resolver import DualSplitResolver


def create_resolver(kind: str, dim: int | None = None):
    kind = kind.lower().strip()
    if kind == "standard":
        return StandardResolver()
    if kind == "split":
        if dim is None:
            raise ValueError("dim is required for the split algebra")
        return SplitResolver(dim)
    if kind == "dual":
        #Dual standard for now require no dimension
        #if dim is None:
        #    raise ValueError("dim is required for the split algebra")
        return DualStandardResolver()          # dual over standard parent
    if kind == "dual_split":
        if dim is None:
            raise ValueError("dim is required for the dual_split algebra")
        return DualSplitResolver(dim)          # future: dual over split parent
    raise ValueError(f"Unknown algebra kind: {kind!r}")
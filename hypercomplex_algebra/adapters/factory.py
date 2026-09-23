"""Factory for building resolvers from an algebra kind + config."""
from ..core.base.resolver import BasisProductResolver
from ..core.tensor.resolver import TensorResolver
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
        return DualStandardResolver()
    if kind == "dual_split":
        if dim is None:
            raise ValueError("dim is required for the dual_split algebra")
        return DualSplitResolver(dim)
    raise ValueError(f"Unknown algebra kind: {kind!r}")


def create_tensor_resolver(slots):
    """Build a TensorResolver from a list of slot specs.

    Each slot is either a kind string ("standard") or a (kind, dim) tuple
    (("split", 2)). Standard slots ignore dim; split slots require it.
    """
    slot_resolvers = []
    for slot in slots:
        if isinstance(slot, (tuple, list)):
            kind = slot[0]
            dim = slot[1] if len(slot) > 1 else None
        else:
            kind, dim = slot, None
        slot_resolvers.append(create_resolver(kind, dim))
    return TensorResolver(slot_resolvers)
"""Core contract for resolving basis element products (innermost layer)."""
from abc import ABC, abstractmethod


class BasisProductResolver(ABC):
    """Resolves e_i * e_j = sign * e_index.

    The domain (SparseMultiplier) depends only on this abstraction,
    never on a concrete engine.
    """

    @abstractmethod
    def resolve(self, i: int, j: int) -> tuple[int, int]:
        """Return (sign, index) for e_i * e_j, sign in {+1, -1}."""
        raise NotImplementedError
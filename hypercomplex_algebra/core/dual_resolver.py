"""Core contract for dual basis product resolution."""
from abc import ABC, abstractmethod


class DualResolver(ABC):
    """Resolves products of dual basis elements.

    A dual basis element is identified by (index, eps_flag).
    The resolver returns (sign, result_index, result_eps_flag),
    or (0, 0, 0) for nilpotent zero products.
    """

    @abstractmethod
    def resolve(self, i: int, eps_i: int, j: int, eps_j: int) -> tuple[int, int, int]:
        raise NotImplementedError
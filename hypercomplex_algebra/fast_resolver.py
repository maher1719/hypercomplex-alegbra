"""Adapter: resolves basis products via hypercomplex-engine's O(1) engine.

This is the ONLY module that imports hypercomplex.
"""
from hypercomplex import FastStandard

from .resolver import BasisProductResolver


class FastResolver(BasisProductResolver):
    def __init__(self):
        self._engine = FastStandard()

    def resolve(self, i: int, j: int) -> tuple[int, int]:
        # Coefficients already carry input signs -> use the sign-free index API.
        return self._engine.multiply_indices(i, j)
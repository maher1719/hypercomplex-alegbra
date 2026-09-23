"""Sparse tensor multiplication. Keys are tuples of indices (one per slot)."""
from .resolver import TensorResolver


class TensorSparseMultiplier:
    """Multiplies two sparse tensor elements.

    Elements are dicts: {(i, j, k, ...): coefficient}
    """

    def __init__(self, resolver: TensorResolver, tolerance: float = 1e-15):
        self._resolver = resolver
        self._tolerance = tolerance

    def multiply(self, a: dict, b: dict) -> dict:
        result: dict = {}
        for key_a, ca in a.items():
            if abs(ca) < self._tolerance:
                continue
            for key_b, cb in b.items():
                if abs(cb) < self._tolerance:
                    continue
                sign, result_key = self._resolver.resolve(key_a, key_b)
                result[result_key] = result.get(result_key, 0.0) + sign * ca * cb
        return {k: c for k, c in result.items() if abs(c) > self._tolerance}
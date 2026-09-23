"""Tensor product resolver: composes per-slot resolvers.

A tensor basis element is a tuple of indices, one per slot. Multiplication
is component-wise: each slot resolves independently with its own algebra's
rules, the signs multiply, and the result indices form a tuple.
"""


class TensorResolver:
    """Composes a list of slot resolvers into a tensor product resolver."""

    def __init__(self, slot_resolvers):
        if not slot_resolvers:
            raise ValueError("TensorResolver requires at least one slot")
        self._slots = list(slot_resolvers)

    @property
    def num_slots(self) -> int:
        return len(self._slots)

    def resolve(self, key_a: tuple, key_b: tuple) -> tuple[int, tuple]:
        """Resolve two multi-slot basis elements.

        key_a, key_b: tuples of indices, one per slot.
        Returns (total_sign, result_key) where result_key is a tuple.
        """
        n = len(self._slots)
        if len(key_a) != n:
            raise ValueError(f"Expected {n} indices, got {len(key_a)} in {key_a}")
        if len(key_b) != n:
            raise ValueError(f"Expected {n} indices, got {len(key_b)} in {key_b}")

        total_sign = 1
        result_key = []
        for resolver, a, b in zip(self._slots, key_a, key_b):
            sign, idx = resolver.resolve(a, b)
            total_sign *= sign
            result_key.append(idx)
        return total_sign, tuple(result_key)
"""Interactive trace of tensor multiplication: signs, indices, coefficients."""
import pytest
from hypercomplex_algebra import (
    ExpressionMultiplier,
    multiply_tensor_expressions,
    multiply_many_tensor_expressions,
)

# Three standard slots (dimension-independent, so any index works)
SLOTS = [("standard", None), ("standard", None), ("standard", None)]


class TestTensorTrace:
    def setup_method(self):
        self.m = ExpressionMultiplier(kind="tensor", slots=SLOTS)

    # --- 1. The mechanism: sign multiplies, indices tuple up ---
    def test_single_slot_negative(self):
        # Only slot 0 is non-trivial: e1*e1 = -e0
        # Slots 1,2: e0*e0 = e0 (identity)
        # Total sign: (-1)(1)(1) = -1, key (0,0,0) -> scalar
        assert self.m.multiply("e[1,0,0]", "e[1,0,0]") == "-1"

    def test_all_three_slots_negative(self):
        # Each slot: e1*e1 = -e0, so three -1 signs
        # Total sign: (-1)(-1)(-1) = -1, key (0,0,0)
        assert self.m.multiply("e[1,1,1]", "e[1,1,1]") == "-1"

    def test_two_slots_negative_cancel(self):
        # Slots 0,1 give -1 each; slot 2 gives +1
        # Total sign: (-1)(-1)(1) = +1, key (0,0,0)
        assert self.m.multiply("e[1,1,0]", "e[1,1,0]") == "1"

    def test_identity_slots_pass_through(self):
        # e0 is identity in every slot, so indices just pass through
        assert self.m.multiply("e[1,0,0]", "e[0,1,0]") == "e[1,1,0]"

    # --- 2. Your example: e[1,3,2] * e[1,4,3] ---
    def test_your_example(self):
        # Slot 0: e1*e1 = -e0      -> sign -1, index 0
        # Slot 1: e3*e4 = ±e_j     -> engine computes
        # Slot 2: e2*e3 = ±e_k     -> engine computes
        # Result: ±e[0, j, k]
        result = self.m.multiply("e[1,3,2]", "e[1,4,3]")
        print(f"\n  e[1,3,2] * e[1,4,3] = {result}")
        # The first index MUST be 0 (from e1*e1=e0), and there's a sign
        assert result.startswith(("e[0,", "-e[0,"))

    # --- 3. Coefficients multiply into the sign ---
    def test_coefficients_multiply(self):
        # 3 * 2 = 6 coefficient; basis gives e[1,1,0]
        assert self.m.multiply("3e[1,0,0]", "2e[0,1,0]") == "6e[1,1,0]"

    def test_negative_coefficient_cancels_sign(self):
        # Input coeff -1, basis sign -1 (from e1*e1) -> they cancel
        # (-1) * (1) * (-1) = +1, key (0,0,0)
        assert self.m.multiply("-e[1,0,0]", "e[1,0,0]") == "1"

    def test_negative_coefficient_compounds(self):
        # Input coeff -2, basis sign -1 -> (-2)(1)(-1) = +2
        assert self.m.multiply("-2e[1,0,0]", "e[1,0,0]") == "2"

    # --- 4. multiply_many with tensors ---
    def test_mm_builds_up_indices(self):
        # e[1,0,0] * e[0,1,0] = e[1,1,0]
        # e[1,1,0] * e[0,0,1] = e[1,1,1]
        result = self.m.multiply_many(["e[1,0,0]", "e[0,1,0]", "e[0,0,1]"])
        assert result == "e[1,1,1]"

    def test_mm_accumulates_signs(self):
        # Each multiply by e[1,0,0] flips slot 0's sign
        # e[1,0,0] * e[1,0,0] = -1  (one flip)
        # -1 * e[1,0,0]... wait, -1 is scalar, scalar*x = -x
        # Let's do: e[1,0,0] three times
        # Step 1: e[1,0,0]*e[1,0,0] = -1 (scalar)
        # Step 2: -1 * e[1,0,0] = -e[1,0,0]
        result = self.m.multiply_many(["e[1,0,0]", "e[1,0,0]", "e[1,0,0]"])
        assert result == "-e[1,0,0]"

    def test_mm_with_coefficients(self):
        result = self.m.multiply_many(["2e[1,0,0]", "3e[0,1,0]"])
        assert result == "6e[1,1,0]"

    # --- 5. Distributivity over sums ---
    def test_distributive(self):
        # (e[1,0,0] + e[0,1,0]) * e[1,0,0]
        # = e[1,0,0]*e[1,0,0] + e[0,1,0]*e[1,0,0]
        # = -1 + e[1,1,0]
        result = self.m.multiply("e[1,0,0] + e[0,1,0]", "e[1,0,0]")
        # Sorted: (0,0,0) with coeff -1, then (1,1,0) with coeff 1
        assert result == "-1 + e[1,1,0]"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])  # -s shows the print output
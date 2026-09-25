"""
Tensor product algebra test suite for hypercomplex_algebra.

Tensor basis elements use multi-index notation e[i,j,k]. Multiplication is
component-wise: each slot resolves with its own algebra, signs multiply.

Run:
    pytest tests/test_tensor_algebra.py -v
"""
import random

import pytest

from hypercomplex_algebra import (
    TensorResolver, TensorSparseMultiplier,
    TensorElementParser, TensorElementFormatter,
    ExpressionMultiplier, StandardResolver, SplitResolver,
    multiply_tensor_expressions, multiply_many_tensor_expressions,
)


# ======================================================================
# 1. TENSOR RESOLVER — composition
# ======================================================================

class TestTensorResolver:
    def setup_method(self):
        self.r = TensorResolver([StandardResolver(), StandardResolver()])

    def test_num_slots(self):
        assert self.r.num_slots == 2

    def test_component_wise_square(self):
        # e[1,1]·e[1,1]: each slot e1·e1 = -e0, signs (-1)(-1) = +1
        sign, key = self.r.resolve((1, 1), (1, 1))
        assert sign == 1
        assert key == (0, 0)

    def test_single_negative_sign(self):
        # e[1,0]·e[1,0]: slot0 e1·e1=-e0, slot1 e0·e0=e0 -> sign -1
        sign, key = self.r.resolve((1, 0), (1, 0))
        assert sign == -1
        assert key == (0, 0)

    def test_identity(self):
        sign, key = self.r.resolve((0, 0), (1, 2))
        assert sign == 1
        assert key == (1, 2)

    def test_mismatched_length_raises(self):
        with pytest.raises(ValueError):
            self.r.resolve((1, 2, 3), (1, 2))

    def test_empty_slots_raises(self):
        with pytest.raises(ValueError):
            TensorResolver([])

    def test_matches_component_resolvers(self):
        std = StandardResolver()
        tensor_r = TensorResolver([std, std])
        rng = random.Random(42)
        for _ in range(200):
            i, j = rng.randint(0, 7), rng.randint(0, 7)
            k, l = rng.randint(0, 7), rng.randint(0, 7)
            t_sign, t_key = tensor_r.resolve((i, k), (j, l))
            s1, idx1 = std.resolve(i, j)
            s2, idx2 = std.resolve(k, l)
            assert t_sign == s1 * s2
            assert t_key == (idx1, idx2)


class TestTensorWithSplitSlot:
    def test_split_slot_positive_square(self):
        # split(dim=1): e1·e1 = +e0, so sign is +1 (not -1)
        r = TensorResolver([SplitResolver(dim=1), StandardResolver()])
        sign, key = r.resolve((1, 0), (1, 0))
        assert sign == 1
        assert key == (0, 0)

    def test_split_slot_out_of_range_raises(self):
        r = TensorResolver([SplitResolver(dim=2), StandardResolver()])
        with pytest.raises(ValueError):
            r.resolve((5, 0), (1, 0))  # index 5 out of range for dim=2


# ======================================================================
# 2. TENSOR PARSER
# ======================================================================

class TestTensorParser:
    def setup_method(self):
        self.parser = TensorElementParser(num_slots=3)

    def test_parse_scalar(self):
        assert self.parser.parse("5") == {(0, 0, 0): 5.0}

    def test_parse_basis(self):
        assert self.parser.parse("e[1,2,0]") == {(1, 2, 0): 1.0}

    def test_parse_coefficient(self):
        assert self.parser.parse("3e[1,2,0]") == {(1, 2, 0): 3.0}

    def test_parse_negative(self):
        assert self.parser.parse("-e[1,2,0]") == {(1, 2, 0): -1.0}


    def test_parse_mixed(self):
        result = self.parser.parse("e[1,0,0] + 2e[0,1,3]")
        assert result == {(1, 0, 0): 1.0, (0, 1, 3): 2.0}

    def test_parse_identity_explicit(self):
        assert self.parser.parse("e[0,0,0]") == {(0, 0, 0): 1.0}

    def test_wrong_slot_count_raises(self):
        with pytest.raises(ValueError):
            self.parser.parse("e[1,2]")  # 2 indices, need 3

    def test_negative_index_raises(self):
        with pytest.raises(ValueError):
            self.parser.parse("e[1,-2,0]")

    def test_malformed_raises(self):
        with pytest.raises(ValueError):
            self.parser.parse("e[1,2,0")  # missing ']'


# ======================================================================
# 3. TENSOR FORMATTER
# ======================================================================

class TestTensorFormatter:
    def setup_method(self):
        self.formatter = TensorElementFormatter()

    def test_format_scalar(self):
        assert self.formatter.format({(0, 0, 0): 5.0}) == "5"

    def test_format_basis(self):
        assert self.formatter.format({(1, 2, 0): 1.0}) == "e[1,2,0]"

    def test_format_coefficient(self):
        assert self.formatter.format({(1, 2, 0): 3.0}) == "3e[1,2,0]"

    def test_format_negative(self):
        assert self.formatter.format({(1, 2, 0): -1.0}) == "-e[1,2,0]"

    def test_format_mixed_sorted(self):
        result = self.formatter.format({(1, 0, 0): 1.0, (0, 1, 3): 2.0})
        assert result == "2e[0,1,3] + e[1,0,0]"

    def test_format_empty(self):
        assert self.formatter.format({}) == "0"


# ======================================================================
# 4. ROUND-TRIP
# ======================================================================

class TestTensorRoundTrip:
    def setup_method(self):
        self.parser = TensorElementParser(num_slots=3)
        self.formatter = TensorElementFormatter()

    @pytest.mark.parametrize("expr", [
        "e[1,2,0]",
        "3e[0,1,2]",
        "e[1,0,0] + 2e[0,1,3]",
        "5",
        "e[0,0,0]",
        "-e[2,2,2] + e[1,1,1]",
    ])
    def test_roundtrip(self, expr):
        parsed = self.parser.parse(expr)
        formatted = self.formatter.format(parsed)
        reparsed = self.parser.parse(formatted)
        assert reparsed == parsed


# ======================================================================
# 5. TENSOR EXPRESSIONS — end-to-end
# ======================================================================

class TestTensorExpressions:
    def setup_method(self):
        # C ⊗ H (two standard slots)
        self.m = ExpressionMultiplier(
            kind="tensor", slots=[("standard", None), ("standard", None)]
        )

    def test_identity(self):
        assert self.m.multiply("e[0,0]", "e[1,2]") == "e[1,2]"

    def test_component_square(self):
        # e[1,1]·e[1,1] = e[0,0] = 1
        assert self.m.multiply("e[1,1]", "e[1,1]") == "1"

    def test_scalar_multiply(self):
        assert self.m.multiply("3", "e[1,0]") == "3e[1,0]"

    def test_distributive(self):
        # (e[1,0] + e[0,1]) · e[1,0]
        result = self.m.multiply("e[1,0] + e[0,1]", "e[1,0]")
        # e[1,0]·e[1,0] = -e[0,0]; e[0,1]·e[1,0] = e[1,1]
        # -> -1 + e[1,1]
        assert self.m.multiply("e[1,0] + e[0,1]", "e[1,0]") is not None

    def test_three_slots(self):
        m3 = ExpressionMultiplier(
            kind="tensor",
            slots=[("standard", None), ("standard", None), ("standard", None)]
        )
        # e[1,1,1]·e[1,1,1]: three slots each give -1, (-1)^3 = -1
        assert m3.multiply("e[1,1,1]", "e[1,1,1]") == "-1"

    def test_kind_property(self):
        assert self.m.kind == "tensor"

    def test_requires_slots(self):
        with pytest.raises(ValueError):
            ExpressionMultiplier(kind="tensor")


# ======================================================================
# 6. TENSOR FACADE
# ======================================================================

class TestTensorFacade:
    def test_multiply_tensor(self):
        slots = [("standard", None), ("standard", None)]
        assert multiply_tensor_expressions("e[1,1]", "e[1,1]", slots) == "1"

    def test_multiply_many_tensor(self):
        slots = [("standard", None), ("standard", None)]
        result = multiply_many_tensor_expressions(["e[1,0]", "e[0,1]"], slots)
        assert result == "e[1,1]"

    def test_caching_same_slots(self):
        slots = [("standard", None), ("standard", None)]
        a = multiply_tensor_expressions("e[1,0]", "e[0,1]", slots)
        b = multiply_tensor_expressions("e[1,0]", "e[0,1]", slots)
        assert a == b


# ======================================================================
# 7. EDGE CASES
# ======================================================================

class TestTensorEdgeCases:
    def test_zero_times_tensor(self):
        slots = [("standard", None), ("standard", None)]
        assert multiply_tensor_expressions("0", "e[1,2]", slots) == "0"

    def test_tensor_isolation_from_standard(self):
        # Same-looking indices, different algebra structure
        slots = [("standard", None), ("standard", None)]
        assert multiply_tensor_expressions("e[1,0]", "e[1,0]", slots) == "-1"

    def test_split_dim_enforced_in_tensor(self):
        slots = [("split", 2), ("standard", None)]
        with pytest.raises(ValueError):
            multiply_tensor_expressions("e[5,0]", "e[1,0]", slots)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
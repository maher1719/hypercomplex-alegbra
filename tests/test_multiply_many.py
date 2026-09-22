"""
Multi-expression multiplication (MM) and its composition with ME.

Covers:
    1. Left-fold correctness      — MM == nested left ME
    2. Non-associativity          — octonions: (ab)c != a(bc)
    3. Non-commutativity          — ab != ba
    4. Composition of groups      — ME(MM(a,b,c), MM(d,e))
    5. Zero short-circuit
    6. Single-element identity
    7. Empty raises
    8. Split 'sisters'            — MM & ME share one dim rule
"""

import pytest

from hypercomplex_algebra import (
    ExpressionMultiplier,
    multiply_expressions,
    multiply_many_expressions,
    multiply_many_split_expressions,
    multiply_split_expressions,
)


class TestLeftFold:
    def test_mm_equals_left_nested_me(self):
        a, b, c = "e1", "e2", "e3"
        mm = multiply_many_expressions([a, b, c])
        nested = multiply_expressions(multiply_expressions(a, b), c)
        assert mm == nested

    def test_mm_four_elements(self):
        mm = multiply_many_expressions(["e1", "e2", "e3", "e4"])
        manual = multiply_expressions(
            multiply_expressions(multiply_expressions("e1", "e2"), "e3"),
            "e4",
        )
        assert mm == manual


class TestNonAssociativity:
    def test_octonions_non_associative(self):
        # Classic octonion case: (e1*e2)*e4 = +e7, but e1*(e2*e4) = -e7
        left_fold = multiply_many_expressions(["e1", "e2", "e4"])
        right_nested = multiply_expressions("e1", multiply_expressions("e2", "e4"))
        assert left_fold == "e7"
        assert right_nested == "-e7"
        assert left_fold != right_nested  # genuinely non-associative


class TestNonCommutativity:
    def test_order_matters(self):
        assert multiply_expressions("e1", "e2") == "e3"
        assert multiply_expressions("e2", "e1") == "-e3"
        assert multiply_expressions("e1", "e2") != multiply_expressions("e2", "e1")


class TestComposition:
    def test_group_composition_matches_nesting(self):
        # ME(MM(a,b,c), MM(d,e)) == explicit nesting of the same bracketing
        a, b, c, d, e = "e1", "e2", "e3", "e4", "e5"
        left_group = multiply_many_expressions([a, b, c])
        right_group = multiply_many_expressions([d, e])
        via_composition = multiply_expressions(left_group, right_group)
        via_nesting = multiply_expressions(
            multiply_expressions(multiply_expressions(a, b), c),
            multiply_expressions(d, e),
        )
        assert via_composition == via_nesting


class TestEdgeCases:
    def test_zero_short_circuit(self):
        assert multiply_many_expressions(["e1", "0", "e2"]) == "0"

    def test_single_element_identity(self):
        assert multiply_many_expressions(["3e1 + 2e2"]) == "3e1 + 2e2"

    def test_empty_raises(self):
        with pytest.raises(ValueError):
            multiply_many_expressions([])

    def test_coefficients_fold_correctly(self):
        # (2e1)*(3e1) = 6*(e1*e1) = 6*(-1) = -6
        assert multiply_many_expressions(["2e1", "3e1"]) == "-6"


class TestSplitSisters:
    def test_mm_and_me_share_dim_rule(self):
        # MM of two elements == ME of those two elements (same dim)
        mm = multiply_many_split_expressions(["e1", "e2"], dim=2)
        me = multiply_split_expressions("e1", "e2", dim=2)
        assert mm == me

    def test_mm_respects_split_dim(self):
        # e5 needs dim>=3, resolver pinned to dim=2 -> raise
        with pytest.raises(ValueError):
            multiply_many_split_expressions(["e5", "e1"], dim=2)

    def test_me_respects_split_dim(self):
        with pytest.raises(ValueError):
            multiply_split_expressions("e5", "e1", dim=2)

    def test_split_mm_within_dim(self):
        # split dim=2: e2 is a split element, e2*e2 = +1
        assert multiply_many_split_expressions(["e2", "e2"], dim=2) == "1"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
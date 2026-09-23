"""
Tensor Mega Test: Exhaustive cross-validation.

We don't just test random samples; we generate the entire Cartesian product 
of basis elements for various tensor configurations and verify that the 
TensorResolver and TensorSparseMultiplier perfectly match the mathematical 
ground truth (component-wise resolution).

Run:
    pytest tests/test_tensor_mega.py -v
"""
import itertools
import pytest

from hypercomplex_algebra import (
    TensorResolver, TensorSparseMultiplier,
    StandardResolver, SplitResolver,
    ExpressionMultiplier,
)


def build_ground_truth_resolvers(slots_config):
    """Helper to build the proven component resolvers and their index limits."""
    comp_resolvers = []
    limits = []
    for kind, dim in slots_config:
        if kind == "standard":
            comp_resolvers.append(StandardResolver())
            limits.append(8)  # Test up to octonions (indices 0..7)
        elif kind == "split":
            comp_resolvers.append(SplitResolver(dim))
            limits.append(1 << dim)
        else:
            raise ValueError(f"Unsupported slot kind for mega test: {kind}")
    return comp_resolvers, limits


class TestTensorMegaResolver:
    """Exhaustive validation of TensorResolver against component resolvers."""

    @pytest.mark.parametrize("slots_config", [
        # 2 slots: C x H (Standard x Standard)
        [("standard", None), ("standard", None)],
        # 2 slots: Split(dim=2) x Standard
        [("split", 2), ("standard", None)],
        # 3 slots: C x H x O (all standard)
        [("standard", None), ("standard", None), ("standard", None)],
        # 3 slots: Split(1) x Split(2) x Standard
        [("split", 1), ("split", 2), ("standard", None)],
        # 4 slots: The ultimate stress test
        [("standard", None), ("standard", None), ("standard", None), ("standard", None)],
    ])
    def test_exhaustive_resolver_cross_product(self, slots_config):
        comp_resolvers, limits = build_ground_truth_resolvers(slots_config)
        tensor_r = TensorResolver(comp_resolvers)

        # Generate every possible basis key for this tensor
        index_ranges = [range(limit) for limit in limits]
        all_keys = list(itertools.product(*index_ranges))

        # Test every single pair (N^2 operations)
        for key_a in all_keys:
            for key_b in all_keys:
                # 1. Ground truth: component-wise resolution
                expected_sign = 1
                expected_indices = []
                for resolver, i, j in zip(comp_resolvers, key_a, key_b):
                    s, idx = resolver.resolve(i, j)
                    expected_sign *= s
                    expected_indices.append(idx)
                expected_key = tuple(expected_indices)

                # 2. Actual: TensorResolver
                actual_sign, actual_key = tensor_r.resolve(key_a, key_b)

                # 3. Assert absolute perfection
                assert actual_sign == expected_sign, f"Sign mismatch for {key_a}*{key_b}"
                assert actual_key == expected_key, f"Key mismatch for {key_a}*{key_b}"


class TestTensorMegaMultiplier:
    """Exhaustive validation of TensorSparseMultiplier dict logic."""

    @pytest.mark.parametrize("slots_config", [
        [("standard", None), ("standard", None)],
        [("split", 2), ("standard", None)],
        [("split", 1), ("split", 1), ("standard", None)],
    ])
    def test_exhaustive_multiplier_cross_product(self, slots_config):
        comp_resolvers, limits = build_ground_truth_resolvers(slots_config)
        
        # Keep limits slightly smaller for the multiplier to avoid massive O(N^4) loops
        # (e.g. 4x4x4 = 64 keys -> 4096 pairs is plenty for dict validation)
        limits = [min(lim, 4) for lim in limits] 
        
        tensor_r = TensorResolver(comp_resolvers)
        mult = TensorSparseMultiplier(tensor_r)

        index_ranges = [range(limit) for limit in limits]
        all_keys = list(itertools.product(*index_ranges))

        for key_a in all_keys:
            for key_b in all_keys:
                a = {key_a: 1.0}
                b = {key_b: 1.0}
                result = mult.multiply(a, b)

                # Compute expected dict result
                exp_sign = 1
                exp_idx = []
                for resolver, i, j in zip(comp_resolvers, key_a, key_b):
                    s, idx = resolver.resolve(i, j)
                    exp_sign *= s
                    exp_idx.append(idx)
                exp_key = tuple(exp_idx)

                if exp_sign == 0:
                    assert not result, f"Expected zero for {key_a}*{key_b}, got {result}"
                else:
                    assert result == {exp_key: float(exp_sign)}, \
                        f"Dict mismatch for {key_a}*{key_b}: expected {exp_key}:{exp_sign}, got {result}"


class TestTensorMegaExpressions:
    """End-to-end string multiplication stress tests."""

    def test_massive_distributive_expansion(self):
        # (e[1,0] + e[0,1] + e[1,1]) * (e[1,0] + e[0,1])
        # This forces the multiplier to handle 3x2 = 6 term expansions, 
        # combining like terms and resolving signs correctly.
        m = ExpressionMultiplier(
            kind="tensor", 
            slots=[("standard", None), ("standard", None)]
        )
        
        a = "e[1,0] + e[0,1] + e[1,1]"
        b = "e[1,0] + e[0,1]"
        result = m.multiply(a, b)
        
        # We don't even need to hardcode the exact string, we just verify 
        # it parses back into the exact mathematical truth.
        # e[1,0]*e[1,0] = -1
        # e[1,0]*e[0,1] = e[1,1]
        # e[0,1]*e[1,0] = e[1,1]
        # e[0,1]*e[0,1] = -1
        # e[1,1]*e[1,0] = e[0,1] (since e1*e1=-1, e1*e0=e1 -> -e[0,1])
        # e[1,1]*e[0,1] = e[1,0] (since e1*e0=e1, e1*e1=-1 -> -e[1,0])
        
        # Total: -1 + e[1,1] + e[1,1] - 1 - e[0,1] - e[1,0]
        #      = -2 - e[1,0] - e[0,1] + 2e[1,1]
        
        parsed = m._parser.parse(result)
        assert parsed[(0,0)] == -2.0
        assert parsed[(1,0)] == -1.0
        assert parsed[(0,1)] == -1.0
        assert parsed[(1,1)] == 2.0

    def test_mm_long_chain(self):
        m = ExpressionMultiplier(
            kind="tensor", 
            slots=[("standard", None), ("standard", None)]
        )
        # Multiply e[1,0] eight times. 
        # e1^8 = (e1^2)^4 = (-1)^4 = 1
        result = m.multiply_many(["e[1,0]"] * 8)
        assert result == "1"

    def test_mm_split_sign_flips(self):
        m = ExpressionMultiplier(
            kind="tensor", 
            slots=[("split", 1), ("standard", None)]
        )
        # split e1^2 = +1. standard e1^2 = -1.
        # e[1,1] * e[1,1] -> (+1)*(-1) = -1
        result = m.multiply("e[1,1]", "e[1,1]")
        assert result == "-1"
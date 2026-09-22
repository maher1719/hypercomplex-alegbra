from hypercomplex_algebra import multiply_expressions

# Complex-like: (1 + e1)^2 = 1 + 2e1 + e1^2 = 1 + 2e1 - 1 = 2e1
assert multiply_expressions("1 + e1", "1 + e1") == "2e1"

# Quaternion: e1 * e2 = e3
assert multiply_expressions("e1", "e2") == "e3"

# Coefficients carry signs: (2e1) * (-3e2) = -6 e3
assert multiply_expressions("2e1", "-3e2") == "-6e3"

# High index, no dense array, no ceiling: e5000 * e5000 = -e0
assert multiply_expressions("e5000", "e5000") == "-1"
#print (multiply_expressions("1 + e1 + 3e2 - 12e33", "e"))
print(multiply_expressions("0.6e0", "-0.3e5000"))
print("All smoke tests passed.")

from hypercomplex_algebra import multiply_split_expressions, ExpressionMultiplier

# split-complex (dim=1): e1^2 = +1  (not -1 like standard)
assert multiply_split_expressions("e1", "e1", dim=1) == "1"

# mixing split dims raises
m2 = ExpressionMultiplier(kind="split", dim=2)
try:
    m2.multiply("e5", "e1")   # index 5 needs dim>=3, but resolver is pinned to dim=2
    assert False, "should have raised"
except ValueError as e:
    print("correctly raised:", e)




from hypercomplex_algebra import ExpressionMultiplier

m = ExpressionMultiplier(kind="split", dim=2)

# default: enforce_check=True -> logs the check
m.multiply_many(["e1", "e2"])
# INFO MM check: all 2 expressions valid

m.multiply_many(["e1", "0", "e2"])
# INFO MM check: all 3 expressions valid
# INFO MM check: product became zero; short-circuiting (all 3 expressions were validated)

# skip the check
fast = ExpressionMultiplier(kind="split", dim=2, enforce_check=False)
print(fast.multiply_many(["e1", "e3"]))   # no check, no logs
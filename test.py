from hypercomplex_algebra import multiply_expressions

# Complex-like: (1 + e1)^2 = 1 + 2e1 + e1^2 = 1 + 2e1 - 1 = 2e1
assert multiply_expressions("1 + e1", "1 + e1") == "2e1"

# Quaternion: e1 * e2 = e3
assert multiply_expressions("e1", "e2") == "e3"

# Coefficients carry signs: (2e1) * (-3e2) = -6 e3
assert multiply_expressions("2e1", "-3e2") == "-6e3"

# High index, no dense array, no ceiling: e5000 * e5000 = -e0
assert multiply_expressions("e5000", "e5000") == "-1"
print (multiply_expressions("1 + e1 + 3e2 - 12e33", "e"))
print(multiply_expressions("0.6e0", "-0.3e5000"))
print("All smoke tests passed.")
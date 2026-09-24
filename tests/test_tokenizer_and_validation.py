"""Tests for the tokenizer rewrite and the removal of enforce_check.

The old naive tokenizer split on every bare '+'/'-', which tore apart
scientific-notation-lookalikes ("1e-3"), signed-index attempts ("e-1"),
and bracketed tensor indices ("e[-1,0]") before the specific, helpful
error checks in each parser ever got to see the whole term. This meant
those checks were effectively dead code, reachable only in tests that
called the parser's internal method directly, never through the public
string API.

ExpressionMultiplier no longer has an enforce_check parameter: every
expression is always parsed and range-validated up front, in
multiply_many, before any multiplication happens.
"""
import pytest

from hypercomplex_algebra import (
    ElementParser, DualElementParser, TensorElementParser,
    ExpressionMultiplier, multiply_many_split_expressions,
)


class TestTokenizerReachesTheRealChecks:
    def test_negative_standard_index_is_caught_with_its_own_message(self):
        # Previously: tokenizer split "e-1" into "+e" and "-1", and the
        # first fragment failed with a generic int-parse error before the
        # dedicated "nothing recognizable after 'e'" check ever ran.
        with pytest.raises(ValueError, match="non-negative"):
            ElementParser().parse("e-1")

    def test_negative_dual_index_is_caught_with_its_own_message(self):
        with pytest.raises(ValueError, match="Basis index must be >= 0"):
            DualElementParser().parse("eps_e-1")

    def test_negative_tensor_index_reports_the_real_problem(self):
        # Previously: reported "missing bracket ']'", which was false —
        # the bracket was there, just torn away from its own content.
        with pytest.raises(ValueError, match="[Ii]ndices must be >= 0"):
            TensorElementParser(2).parse("e[-1,0]")

    def test_scientific_notation_attempt_gives_one_clear_message(self):
        # Lowercase 'e' is reserved for the basis letter, so "1e-3" is
        # rejected as ambiguous. Uppercase 'E' is ordinary float notation
        # and is NOT reserved, so "1E-3" correctly parses as the scalar
        # 0.001 (on e0) — this only works now that the tokenizer keeps
        # "1E-3" as one piece instead of tearing it apart at the '-'.
        for bad in ("1e-3", "e-3"):
            with pytest.raises(ValueError, match="non-negative"):
                ElementParser().parse(bad)
        assert ElementParser().parse("1E-3") == {0: 0.001}


class TestBracketsSurviveTokenizing:
    def test_tensor_expression_with_internal_minus_is_one_term(self):
        # "e[-1,0]" must tokenize as ONE body, not be split at the '-'
        # inside the brackets.
        with pytest.raises(ValueError) as exc:
            TensorElementParser(2).parse("e[-1,0]")
        assert "missing" not in str(exc.value).lower()

    def test_valid_tensor_expression_still_parses(self):
        assert TensorElementParser(2).parse("e[1,2]") == {(1, 2): 1.0}
        assert TensorElementParser(2).parse("3e[1,2] - e[0,0]") == {(1, 2): 3.0, (0, 0): -1.0}


class TestStrictOperatorSyntax:
    """Doubled and trailing operators are syntax errors, not silently
    normalised. A trailing '+' most often means a forgotten second term."""

    @pytest.mark.parametrize("expr", ["e1++e2", "e1--e2", "e1+", "e1-", "+", "-", "++e1"])
    def test_malformed_operator_sequences_are_rejected(self, expr):
        with pytest.raises(ValueError):
            ElementParser().parse(expr)

    def test_ordinary_expressions_still_parse(self):
        assert ElementParser().parse("e1 - e2 + 3e0") == {1: 1.0, 2: -1.0, 0: 3.0}
        assert ElementParser().parse("-e1") == {1: -1.0}


class TestNoFastPath:
    def test_expression_multiplier_has_no_enforce_check_parameter(self):
        import inspect
        params = inspect.signature(ExpressionMultiplier.__init__).parameters
        assert "enforce_check" not in params

    def test_out_of_range_term_is_always_caught_even_after_a_zero(self):
        # This used to depend on enforce_check; now it's simply always true.
        with pytest.raises(ValueError):
            multiply_many_split_expressions(["e1", "0", "e99"], dim=2)

    def test_out_of_range_message_is_specific(self):
        try:
            multiply_many_split_expressions(["e1", "e99"], dim=2)
            assert False, "should have raised"
        except ValueError as e:
            msg = str(e)
            assert msg != "unsupported format", "the real diagnosis must not be swallowed"
            assert "dim=2" in msg

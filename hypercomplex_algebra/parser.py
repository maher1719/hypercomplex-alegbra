"""Parse expression strings into {index: coefficient}."""
import re


class ExpressionParser:
    """Parses '3e0 - 2.34e1 + e2' into {0: 3.0, 1: -2.34, 2: 1.0}.

    Integer basis notation only (e0, e1, e5, ...). Implicit ±1 coefficients
    supported: 'e2' == '1e2', '-e3' == '-1e3'. Note: 'e' always marks a basis
    element, so scientific-notation coefficients (1e-3) are not supported —
    write 0.001 instead.
    """

    _TOKEN_RE = re.compile(r'[+-][^+-]+')

    def parse(self, s: str) -> dict[int, float]:
        s = s.replace(" ", "").replace("\t", "")
        if not s:
            raise ValueError("Empty expression")
        if s[0] not in "+-":
            s = "+" + s

        terms: dict[int, float] = {}
        for token in self._TOKEN_RE.findall(s):
            sign = -1.0 if token[0] == "-" else 1.0
            coeff, index = self._parse_body(token[1:])
            terms[index] = terms.get(index, 0.0) + sign * coeff

        return {i: c for i, c in terms.items() if abs(c) > 1e-15}

    @staticmethod
    def _parse_body(body: str) -> tuple[float, int]:
        if 'e' in body:
            coeff_str, index_str = body.split('e', 1)
            if index_str.lstrip("+-") == "":
                raise ValueError(
                    f"Cannot parse '{body}...': scientific-notation coefficients "
                    f"(like 1e-3) are not supported because 'e' marks a basis "
                    f"element. Use decimal form instead (e.g., 0.001)."
                )
            if index_str == "":
                raise ValueError(f"Element must have basis number but {body} was given.")
            
            magnitude = 1.0 if coeff_str == "" else float(coeff_str)
            index = int(index_str)
        else:
            magnitude = float(body)
            index = 0
        if index < 0:
            raise ValueError(f"Basis index must be >= 0, got {index}")
        return magnitude, index

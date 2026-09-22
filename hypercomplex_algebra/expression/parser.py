from .tokenizer import tokenize


class ElementParser:
    """Parses expressions for standard/split algebras. No epsilon concept."""

    _PRUNE = 1e-15

    def parse(self, s: str) -> dict[int, float]:
        terms: dict[int, float] = {}
        for sign, body in tokenize(s):
            coeff, index = self._parse_body(body)
            terms[index] = terms.get(index, 0.0) + sign * coeff
        return {i: c for i, c in terms.items() if abs(c) > self._PRUNE}

    @staticmethod
    def _parse_body(body: str) -> tuple[float, int]:
        """Returns (coefficient, index). 2-tuple — no eps for base algebras."""
        if 'e' in body:
            coeff_str, index_str = body.split('e', 1)
            if not index_str or index_str[0] in "+-":
                raise ValueError(
                    f"Cannot parse '{body}': scientific-notation coefficients "
                    f"(like 1e-3) are not supported. Use decimal form (e.g., 0.001)."
                )
            magnitude = 1.0 if coeff_str == "" else float(coeff_str)
            index = int(index_str)
        else:
            magnitude = float(body)
            index = 0
        if index < 0:
            raise ValueError(f"Basis index must be >= 0, got {index}")
        return magnitude, index
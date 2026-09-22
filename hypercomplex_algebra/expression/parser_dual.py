from .tokenizer import tokenize


class DualElementParser:
    """Parses expressions for dual/dual_split algebras. Recognizes eps tokens."""

    _PRUNE = 1e-15

    def parse(self, s: str) -> dict[tuple[int, int], float]:
        terms: dict[tuple[int, int], float] = {}
        for sign, body in tokenize(s):
            coeff, index, eps = self._parse_body(body)
            key = (index, eps)
            terms[key] = terms.get(key, 0.0) + sign * coeff
        return {k: c for k, c in terms.items() if abs(c) > self._PRUNE}

    @staticmethod
    def _parse_body(body: str) -> tuple[float, int, int]:
        """Returns (coefficient, index, eps_flag). 3-tuple — dual-aware."""
        # Bare "eps" means ε·e₀
        if body == "eps":
            return 1.0, 0, 1

        # Dual element: eps_e{n}
        if "eps_e" in body:
            coeff_str, index_str = body.split("eps_e", 1)
            magnitude = 1.0 if coeff_str == "" else float(coeff_str)
            index = int(index_str)
            if index < 0:
                raise ValueError(f"Basis index must be >= 0, got {index}")
            return magnitude, index, 1

        # Base element: e{n}  (eps_flag = 0)
        if "e" in body:
            coeff_str, index_str = body.split("e", 1)
            if not index_str or index_str[0] in "+-":
                raise ValueError(
                    f"Cannot parse '{body}': scientific-notation coefficients "
                    f"are not supported. Use decimal form (e.g., 0.001)."
                )
            magnitude = 1.0 if coeff_str == "" else float(coeff_str)
            index = int(index_str)
            if index < 0:
                raise ValueError(f"Basis index must be >= 0, got {index}")
            return magnitude, index, 0

        # Pure scalar
        return float(body), 0, 0
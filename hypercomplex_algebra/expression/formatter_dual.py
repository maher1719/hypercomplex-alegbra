"""Format {index: coefficient} back into an expression string."""


class DualElementFormatter:
    """Formats {index: coefficient} into strings like '3 - 2.34e1 + e2'."""

    def __init__(self, tolerance: float = 1e-15):
        self._tolerance = tolerance

    def format(self, terms: dict[tuple[int, int], float]) -> str:
        # Split into base part (no eps) and dual part (with eps)
        base_terms = [
            (idx, c) for (idx, eps), c in terms.items()
            if eps == 0 and abs(c) > self._tolerance
        ]
        dual_terms = [
            (idx, c) for (idx, eps), c in terms.items()
            if eps == 1 and abs(c) > self._tolerance
        ]

        # Sort each part independently by index
        base_terms.sort(key=lambda item: item[0])
        dual_terms.sort(key=lambda item: item[0])

        # Base part first, then dual part  (canonical form: a + ε·b)
        ordered = base_terms + dual_terms
        if not ordered:
            return "0"

        parts = []
        for pos, (idx, coeff) in enumerate(ordered):
            eps_flag = 0 if pos < len(base_terms) else 1
            body = self._magnitude(idx, abs(coeff), eps_flag)
            if pos == 0:
                parts.append(f"-{body}" if coeff < 0 else body)
            else:
                parts.append(f"- {body}" if coeff < 0 else f"+ {body}")
        return " ".join(parts)

    def _magnitude(self, index: int, mag: float, eps_flag: int = 0) -> str:
        """Format |coefficient| * basis without sign."""
        if eps_flag == 0:
            if index == 0:
                return f"{mag:.10g}"    # pure scalar
            basis = f"e{index}"
        else:
            if index == 0:
                basis = "eps"           # uniform shorthand for ε·e₀
            else:
                basis = f"eps_e{index}"

        if abs(mag - 1.0) < self._tolerance:
            return basis
        return f"{mag:.10g}{basis}"
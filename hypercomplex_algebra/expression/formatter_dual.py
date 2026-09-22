"""Format {index: coefficient} back into an expression string."""


class DualElementFormatter:
    """Formats {index: coefficient} into strings like '3 - 2.34e1 + e2'."""

    def __init__(self, tolerance: float = 1e-15):
        self._tolerance = tolerance

    def format(self, terms: dict[tuple[int, int], float]) -> str:
        items = sorted(
            (key, c) for key, c in terms.items() if abs(c) > self._tolerance
        )
        if not items:
            return "0"

        parts = []
        for pos, (key, coeff) in enumerate(items):
            index, eps_flag = key                      # ← unpack the tuple
            body = self._magnitude(index, abs(coeff), eps_flag)   # ← pass eps_flag
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
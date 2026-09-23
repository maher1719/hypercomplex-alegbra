"""Format {index: coefficient} back into an expression string."""


class ElementFormatter:
    """Formats {index: coefficient} into strings like '3 - 2.34e1 + e2'."""

    def __init__(self, tolerance: float = 1e-15):
        self._tolerance = tolerance

    def format(self, terms: dict[int, float]) -> str:
        items = sorted((i, c) for i, c in terms.items() if abs(c) > self._tolerance)
        if not items:
            return "0"

        parts = []
        for pos, (idx, coeff) in enumerate(items):
            body = self._magnitude(idx, abs(coeff))
            if pos == 0:
                parts.append(f"-{body}" if coeff < 0 else body)
            else:
                parts.append(f"- {body}" if coeff < 0 else f"+ {body}")
        return " ".join(parts)

    def _magnitude(self, index: int, mag: float) -> str:
        if index == 0:
            return f"{mag:.10g}"
        if abs(mag - 1.0) < self._tolerance:
            return f"e{index}"
        return f"{mag:.10g}e{index}"
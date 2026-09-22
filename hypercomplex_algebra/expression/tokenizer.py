import re


def tokenize(s: str) -> list[tuple[float, str]]:
    """Split an expression into (sign, body) pairs. Shared by all parsers."""
    s = s.replace(" ", "").replace("\t", "")
    if not s:
        raise ValueError("Empty expression")
    if s[0] not in "+-":
        s = "+" + s
    result = []
    for token in re.findall(r'[+-][^+-]+', s):
        sign = -1.0 if token[0] == "-" else 1.0
        result.append((sign, token[1:]))
    return result
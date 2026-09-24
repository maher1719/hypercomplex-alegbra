import re

_WHITESPACE = re.compile(r"\s")


def tokenize(s: str) -> list[tuple[float, str]]:
    """Split an expression into (sign, body) pairs. Shared by all parsers.

    A '+' or '-' starts a new term unless it is either:
      - immediately preceded by 'e' (so a mistaken scientific-notation
        coefficient like "1e-3", or a mistaken signed index like "e-1",
        stays as ONE body and gets a precise error from the caller instead
        of being torn into two meaningless pieces), or
      - inside a bracketed tensor index list "e[...]" (so "e[-1,0]" stays
        intact and the tensor parser can report the real problem: a
        negative index, not "a missing bracket").

    Consecutive or trailing operators ("e1++e2", "e1+") are rejected
    outright rather than silently collapsed, matching this package's
    zero-tolerance-for-silent-faults policy.
    """
    s = _WHITESPACE.sub("", s)
    if not s:
        raise ValueError("Empty expression")
    if s[0] not in "+-":
        s = "+" + s

    tokens = []
    i, n = 0, len(s)
    while i < n:
        sign_char = s[i]
        if sign_char not in "+-":
            raise ValueError(
                f"Expected '+' or '-' to start a term at position {i} in {s!r}"
            )
        i += 1
        start = i
        depth = 0
        while i < n:
            c = s[i]
            if c == "[":
                depth += 1
            elif c == "]":
                depth -= 1
                if depth < 0:
                    raise ValueError(f"Unmatched ']' in {s!r}")
            elif c in "+-" and depth == 0 and s[i - 1] not in "eE":
                break
            i += 1
        if depth != 0:
            raise ValueError(f"Unmatched '[' in {s!r}")
        body = s[start:i]
        if not body:
            raise ValueError(
                f"Empty term at position {start} in {s!r} "
                "(check for a doubled or trailing '+'/'-')"
            )
        tokens.append((-1.0 if sign_char == "-" else 1.0, body))
    return tokens
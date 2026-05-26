from __future__ import annotations

import re

from spokenforms.normalizers.numbers import normalize_number_sequence

NATO: dict[str, str] = {
    "alpha": "A",
    "bravo": "B",
    "charlie": "C",
    "delta": "D",
    "echo": "E",
    "foxtrot": "F",
    "golf": "G",
    "hotel": "H",
    "india": "I",
    "juliett": "J",
    "kilo": "K",
    "lima": "L",
    "mike": "M",
    "november": "N",
    "oscar": "O",
    "papa": "P",
    "quebec": "Q",
    "romeo": "R",
    "sierra": "S",
    "tango": "T",
    "uniform": "U",
    "victor": "V",
    "whiskey": "W",
    "xray": "X",
    "x-ray": "X",
    "yankee": "Y",
    "zulu": "Z",
}


def normalize_alphanumeric(value: str) -> str:
    compact = re.sub(r"[^A-Za-z0-9]", "", value)
    if compact:
        return compact.upper()
    pieces: list[str] = []
    for token in re.findall(r"[a-z-]+|\d", value.lower()):
        if token in NATO:
            pieces.append(NATO[token])
        else:
            normalized = normalize_number_sequence(token)
            if normalized:
                pieces.append(normalized)
    return "".join(pieces)

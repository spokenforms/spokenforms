from __future__ import annotations

from typing import Protocol


class Normalizer(Protocol):
    def __call__(self, value: str) -> str:
        raise NotImplementedError

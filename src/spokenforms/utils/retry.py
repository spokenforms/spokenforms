from __future__ import annotations

from collections.abc import Callable


def call_once[T](fn: Callable[[], T]) -> T:
    return fn()

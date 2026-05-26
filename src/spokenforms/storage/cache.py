from __future__ import annotations

from pathlib import Path


def cache_path(directory: Path, key: str) -> Path:
    return directory / f"{key}.json"

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from typing import Any

import orjson
from pydantic import BaseModel


def write_jsonl(path: Path, rows: Sequence[BaseModel]) -> None:
    with path.open("wb") as handle:
        for row in rows:
            payload = orjson.dumps(
                row.model_dump(mode="json"),
                option=orjson.OPT_APPEND_NEWLINE,
            )
            handle.write(payload)


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("rb") as handle:
        for line in handle:
            parsed = orjson.loads(line)
            if isinstance(parsed, dict):
                rows.append(parsed)
    return rows

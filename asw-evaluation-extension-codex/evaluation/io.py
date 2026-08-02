"""Append-only JSONL evidence writers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class JsonlWriter:
    """Write one canonical JSON object per line and flush it immediately."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._stream = path.open("a", encoding="utf-8", newline="\n")

    def write(self, record: dict[str, Any]) -> None:
        self._stream.write(json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n")
        self._stream.flush()

    def close(self) -> None:
        if not self._stream.closed:
            self._stream.flush()
            self._stream.close()

    def __enter__(self) -> "JsonlWriter":
        return self

    def __exit__(self, *_args: Any) -> None:
        self.close()


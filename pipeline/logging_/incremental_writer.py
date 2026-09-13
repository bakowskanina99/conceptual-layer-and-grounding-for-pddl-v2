"""Append-only JSONL writer, flushed after every row -- user's brief:
"Log incrementally, not only at the end of a run -- append to the results
file after every object/variant combination, so a crash partway through does
not lose completed work." One physical write+flush+fsync per row; never
buffered across multiple objects.
"""

from __future__ import annotations

import json
import os
from pathlib import Path


class IncrementalJsonlWriter:
    def __init__(self, path: Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._fh = open(self.path, "a", encoding="utf-8")

    def write_row(self, row: dict) -> None:
        self._fh.write(json.dumps(row, ensure_ascii=False, default=str) + "\n")
        self._fh.flush()
        os.fsync(self._fh.fileno())

    def close(self) -> None:
        self._fh.close()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()


def read_all_rows(path: Path) -> list[dict]:
    """Reads back every row written so far (e.g. to resume/inspect a
    partially-completed run) -- tolerates a truncated final line (a crash
    mid-write) by skipping only that line, not the whole file."""
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return rows

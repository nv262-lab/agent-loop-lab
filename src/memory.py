"""Persistent agent memory — a per-user JSON store.

Memory in this lab is deliberately simple: a flat list of notes keyed by
user. The point of Exercise 2 is that a note written in one run survives
into later runs (slide 12: "memory tampering outlives the session that
caused it"). Each note carries an `origin` tag so that, once students add
provenance in Exercise 3, the agent can tell a user-authored note from one
that was scraped off a web page.

Nothing here talks to a network or a real database.
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import List

STORE = Path(__file__).resolve().parent.parent / "data" / "memory_store.json"


@dataclass
class Note:
    user: str
    text: str
    origin: str = "unknown"          # user | tool_result | web | agent_msg | unknown
    trusted: bool = False            # set by provenance rules in Exercise 3
    ts: float = field(default_factory=time.time)


class Memory:
    def __init__(self, path: Path = STORE):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.write_text("[]")

    def _load(self) -> List[dict]:
        return json.loads(self.path.read_text() or "[]")

    def _save(self, rows: List[dict]) -> None:
        self.path.write_text(json.dumps(rows, indent=2))

    def remember(self, note: Note) -> None:
        rows = self._load()
        rows.append(asdict(note))
        self._save(rows)

    def recall(self, user: str) -> List[Note]:
        return [Note(**r) for r in self._load() if r["user"] == user]

    def wipe(self) -> None:
        """Reset between demo runs."""
        self._save([])

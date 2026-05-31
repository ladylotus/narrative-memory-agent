"""Working memory — current session context buffer."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field

MAX_WINDOW = 10  # rolling window of turns


@dataclass
class Turn:
    role: str  # "user" | "character"
    content: str


class WorkingMemory:
    """Short-term session buffer (Baddeley's central executive + episodic buffer)."""

    def __init__(self, max_window: int = MAX_WINDOW) -> None:
        self._buffer: deque[Turn] = deque(maxlen=max_window)

    def add(self, role: str, content: str) -> None:
        self._buffer.append(Turn(role=role, content=content))

    def get_context(self) -> list[Turn]:
        return list(self._buffer)

    def clear(self) -> None:
        self._buffer.clear()

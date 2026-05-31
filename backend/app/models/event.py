"""Event / episodic memory data models."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class NarrativeEvent:
    """Single tracked event in episodic memory."""

    id: str
    chapter: int
    position: str  # e.g. "3/4" — position within chapter
    protagonist: str
    summary: str
    importance: float = 0.5
    embedding: list[float] | None = None
    related_entities: list[str] = field(default_factory=list)
    zwaan_dims: dict[str, str] = field(default_factory=dict)  # time/space/cause/intent

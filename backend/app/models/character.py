"""Character data models."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Trait:
    name: str
    category: str = "core"  # core | surface | situational
    description: str = ""
    confidence: float = 0.5  # how confident we are about this trait


@dataclass
class CharacterProfile:
    """The semantic memory representation of a character."""

    name: str
    aliases: list[str] = field(default_factory=list)
    traits: list[Trait] = field(default_factory=list)
    relations: dict[str, str] = field(default_factory=dict)  # name → relation
    motivation: str = ""
    arc_stage: str = "unknown"
    embedding_centroid: list[float] | None = None  # semantic center of mass

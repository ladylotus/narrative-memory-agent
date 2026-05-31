"""Semantic memory — character cognitive schemas (traits, relations, patterns)."""

from __future__ import annotations

from typing import Any

from app.models.character import CharacterProfile


class SemanticMemory:
    """Long-term character knowledge — traits, behavior patterns, relations.

    Built and refined during sleep consolidation.
    """

    def __init__(self) -> None:
        self._profiles: dict[str, CharacterProfile] = {}

    def get_profile(self, name: str) -> CharacterProfile | None:
        return self._profiles.get(name)

    def upsert_profile(self, profile: CharacterProfile) -> None:
        self._profiles[profile.name] = profile

    def list_characters(self) -> list[str]:
        return list(self._profiles.keys())

    def get_all_profiles(self) -> dict[str, CharacterProfile]:
        return dict(self._profiles)

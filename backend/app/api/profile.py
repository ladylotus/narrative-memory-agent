"""API endpoints — /profile: character profile."""

from __future__ import annotations

from fastapi import APIRouter

router = APIRouter()


@router.get("/{character_name}")
async def get_profile(character_name: str):
    """Get a character's full cognitive profile."""
    return {
        "status": "not_implemented",
        "character": character_name,
    }


@router.get("/{character_name}/summary")
async def get_profile_summary(character_name: str):
    """Get a character's profile summary (lightweight)."""
    return {"status": "not_implemented", "character": character_name}

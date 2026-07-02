"""API endpoints — /profile: character profile from database."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.database import delete_character, get_character, list_characters

router = APIRouter()


@router.get("/{character_name}")
async def get_profile(character_name: str):
    """Get a character's full cognitive profile."""
    profile = get_character(character_name)
    if profile is None:
        raise HTTPException(status_code=404, detail=f"Character '{character_name}' not found")
    return {
        "status": "ok",
        "character": profile["name"],
        "aliases": profile.get("aliases", []),
        "traits": profile.get("traits", []),
        "relations": profile.get("relations", {}),
        "motivation": profile.get("motivation", ""),
        "arc_stage": profile.get("arc_stage", "unknown"),
        "backstory": profile.get("backstory", ""),
    }


@router.get("/{character_name}/summary")
async def get_profile_summary(character_name: str):
    """Get a character's profile summary (lightweight)."""
    profile = get_character(character_name)
    if profile is None:
        raise HTTPException(status_code=404, detail=f"Character '{character_name}' not found")
    traits = profile.get("traits", [])
    return {
        "status": "ok",
        "character": profile["name"],
        "core_traits": [t["name"] for t in traits if t.get("category") == "core"],
        "arc_stage": profile.get("arc_stage", "unknown"),
    }


@router.delete("/{character_name}")
async def delete_character_endpoint(character_name: str):
    """Delete a character and all associated data."""
    exists = get_character(character_name)
    if exists is None:
        raise HTTPException(status_code=404, detail=f"Character '{character_name}' not found")
    deleted = delete_character(character_name)
    if not deleted:
        raise HTTPException(status_code=500, detail="Failed to delete character")
    return {"status": "ok", "deleted": character_name}


@router.get("/")
async def list_all_characters():
    """List all available characters."""
    names = list_characters()
    return {"status": "ok", "characters": names}

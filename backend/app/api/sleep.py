"""API endpoints — /sleep: trigger consolidation cycle."""

from __future__ import annotations

from fastapi import APIRouter

router = APIRouter()


@router.post("/{character_name}")
async def trigger_sleep(character_name: str):
    """Trigger off-line memory consolidation (Phase 1-2-3)."""
    return {
        "status": "not_implemented",
        "character": character_name,
        "message": "Sleep cycle not implemented yet",
    }


@router.get("/{character_name}/history")
async def get_sleep_history(character_name: str):
    """View consolidation history logs."""
    return {"status": "not_implemented", "character": character_name}

"""API endpoints — /sleep: trigger consolidation cycle."""

from __future__ import annotations

from fastapi import APIRouter

from app.memory.episodic import EpisodicMemory
from app.services.sleep import SleepService

router = APIRouter()
_sleep_service: SleepService | None = None


def _get_service() -> SleepService:
    global _sleep_service
    if _sleep_service is None:
        _sleep_service = SleepService(episodic=EpisodicMemory())
    return _sleep_service


@router.post("/{character_name}")
async def trigger_sleep(character_name: str):
    """Trigger off-line memory consolidation (Phase 1-2-3).

    Analyzes events in episodic memory, detects behavioral conflicts,
    adjusts importance scores, and updates the character's profile.
    Returns a consolidation report.
    """
    service = _get_service()
    result = await service.consolidate(character_name)
    return result


@router.get("/{character_name}/history")
async def get_sleep_history(character_name: str):
    """View consolidation history logs."""
    # Future: persist consolidation logs in DB
    return {
        "status": "ok",
        "character": character_name,
        "message": "History tracking not yet implemented",
        "history": [],
    }

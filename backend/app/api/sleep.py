"""API endpoints — /sleep: trigger consolidation cycle."""

from __future__ import annotations

from fastapi import APIRouter

from app.database import get_character, upsert_character
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
    """Trigger off-line memory consolidation (Phase 1-2-3)."""
    service = _get_service()
    result = await service.consolidate(character_name)

    # Save the report summary to the character record for metacognition injection
    try:
        report = result.get("report", {})
        p2 = report.get("phase2", {})
        p3 = report.get("phase3", {})
        conflicts = report.get("phase1", {}).get("conflicts_detected", [])
        arc_change = p2.get("arc_stage_change")
        summary = p3.get("summary", "")

        lines = []
        if arc_change:
            lines.append(
                f"Arc evolved: {arc_change.get('from', '?')} → "
                f"{arc_change.get('to', '?')} — {arc_change.get('reason', '')}"
            )
        if conflicts:
            for c in conflicts[:3]:  # keep it concise
                lines.append(
                    f"Conflict: intent '{c.get('intent', '?')}' "
                    f"conflicts with trait '{', '.join(c.get('conflicting_keywords', []))}'"
                )
        if summary:
            lines.append(f"Self-audit: {summary[:200]}")

        report_text = "\n".join(lines) if lines else ""
        char = get_character(character_name)
        if char and report_text:
            merged = dict(char)
            merged["last_sleep_report"] = report_text
            upsert_character(merged)
    except Exception:
        pass  # non-blocking

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

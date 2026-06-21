"""API endpoints — /session: cross-session memory management.

Provides:
  - GET /session/resume/{character}  — detect if returning user, return context
  - POST /session/checkpoint         — explicitly save current working memory
  - POST /session/clear              — clear saved state (after sleep, etc.)
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.database import get_character
from app.services.session_resumption import (
    clear_session_state,
    load_session_state,
    save_session_state,
)
from app.api.ask import _get_wm, _sessions

router = APIRouter()


# ── Response models ──────────────────────────────


class ResumeResponse(BaseModel):
    character: str
    has_resumed: bool = False
    turn_count: int = 0
    last_question: str = ""
    preferred_profile: list[float] | None = None


class CheckpointRequest(BaseModel):
    character: str = Field(..., description="Character to checkpoint")
    last_question: str = Field(default="", description="Most recent question asked")


class CheckpointResponse(BaseModel):
    status: str = "ok"
    character: str
    turns_saved: int
    cleared: bool = False


# ── Endpoints ────────────────────────────────────


@router.get("/resume/{character}", response_model=ResumeResponse)
async def resume_session(character: str):
    """Check if a character has saved session state (i.e., was previously active).

    Returns:
      - has_resumed: True if saved state exists
      - turn_count: number of turns in saved working memory
      - last_question: the most recent question
      - preferred_profile: current preference vector (if any)
    """
    state = load_session_state(character)
    if state is None:
        return ResumeResponse(character=character)

    # Also get preferred_profile from character table as authoritative source
    char = get_character(character)
    preferred = None
    if char and char.get("preferred_profile"):
        preferred = char["preferred_profile"]
    elif state.get("preferred_profile"):
        preferred = state["preferred_profile"]

    turns = state.get("turns", [])
    return ResumeResponse(
        character=character,
        has_resumed=True,
        turn_count=len(turns) if isinstance(turns, list) else 0,
        last_question=state.get("last_question", ""),
        preferred_profile=preferred,
    )


@router.post("/checkpoint", response_model=CheckpointResponse)
async def checkpoint_session(body: CheckpointRequest):
    """Save the current working memory state for a character.

    Called automatically on character switch, or explicitly by the frontend
    when the user closes the session.
    """
    if body.character not in _sessions and not body.last_question:
        # No working memory buffer and no question to save — nothing to do
        return CheckpointResponse(
            status="ok",
            character=body.character,
            turns_saved=0,
        )

    wm = _get_wm(body.character) if body.character in _sessions else None
    turns = wm.get_context() if wm else []

    # Get preferred_profile from character table
    char = get_character(body.character)
    preferred = None
    if char:
        preferred = char.get("preferred_profile")

    save_session_state(
        character=body.character,
        working_memory=wm,
        question=body.last_question or None,
        preferred_profile=preferred,
    )

    return CheckpointResponse(
        status="ok",
        character=body.character,
        turns_saved=len(turns),
    )


@router.post("/clear", response_model=CheckpointResponse)
async def clear_session(body: CheckpointRequest):
    """Delete saved session state for a character.

    Called after sleep consolidation to reset the working memory.
    """
    clear_session_state(body.character)

    # Also clear the in-memory buffer if it exists
    if body.character in _sessions:
        _sessions[body.character].clear()

    return CheckpointResponse(
        status="ok",
        character=body.character,
        turns_saved=0,
        cleared=True,
    )

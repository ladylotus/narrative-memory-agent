"""API endpoints — /ask: ask a character."""

from __future__ import annotations

from fastapi import APIRouter

from app.models import AskRequest, AskResponse

router = APIRouter()


@router.post("/", response_model=AskResponse)
async def ask_character(body: AskRequest):
    """Ask a character: Circuit A (generation) + Circuit B (validation)."""
    return AskResponse(
        character=body.character,
        question=body.question,
        options=[],
        status="not_implemented",
    )

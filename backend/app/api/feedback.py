"""API endpoint — /feedback: user marks their preferred option.

Receives the user's choice and mark (why they chose it), then updates
the character's preferred_profile via EMA.

Mark options (from 方案文档.md §九):
  □ 这就是他会做的事      → 角色驱动 → EMA α=0.3
  □ 情节需要这个走向      → 剧情驱动 → 不更新
  □ 想看看这个可能性      → 实验心态 → 不更新
  □ 说不上来，就是感觉    → 默认     → EMA α=0.1
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.database import get_character, upsert_character
from app.services.bias import DIMENSION_KEYS, update_preferred_profile

router = APIRouter()


class FeedbackRequest(BaseModel):
    character: str = Field(..., description="Character name")
    option_label: str = Field(..., description="Label of the chosen option (A/B/C…)")
    scores: dict[str, float] = Field(
        ..., description="T/B/D/C/P scores of the chosen option"
    )
    marks: list[str] = Field(
        default_factory=list,
        description="Why the user chose this option (0-4 strings from the mark options)",
    )


class FeedbackResponse(BaseModel):
    status: str = "ok"
    updated: bool = False
    preferred_profile: list[float] | None = None


@router.post("/", response_model=FeedbackResponse)
async def submit_feedback(body: FeedbackRequest):
    """Receive user option mark → update preferred_profile via EMA."""
    # ── Validate scores ────────────────────────────
    for k in DIMENSION_KEYS:
        if k not in body.scores:
            raise HTTPException(
                status_code=400,
                detail=f"Missing score dimension: {k}. Required: {DIMENSION_KEYS}",
            )

    # ── Get character ──────────────────────────────
    char = get_character(body.character)
    if char is None:
        raise HTTPException(
            status_code=404,
            detail=f"Character '{body.character}' not found",
        )

    # ── EMA update ─────────────────────────────────
    old = char.get("preferred_profile")  # list[float] | None
    result = update_preferred_profile(old, body.scores, body.marks)

    if result["updated"]:
        # Merge: keep existing data, only update preferred_profile
        merged = dict(char)
        merged["preferred_profile"] = result["profile"]
        upsert_character(merged)

    return FeedbackResponse(
        status="ok",
        updated=result["updated"],
        preferred_profile=result["profile"],
    )

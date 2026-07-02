"""API endpoint — /feedback: user marks their preferred option.

Receives the user's choice and mark (why they chose it), then updates
the character's preferred_profile via EMA.

Mark options (from 设计文档.md §九):
  □ role-driven       → character-driven → EMA a=0.3
  □ plot-driven       → plot-driven      → no update
  □ experimental      → experimental     → no update
  □ gut-feeling       → default          → EMA a=0.1
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.database import get_character, upsert_character
from app.memory.episodic import EpisodicMemory
from app.models.event import NarrativeEvent
from app.services.bias import DIMENSION_KEYS, update_preferred_profile
from app.services.session_resumption import save_session_state, load_session_state

router = APIRouter()
episodic = EpisodicMemory()


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

    # ── Write user choice to EpisodicMemory (feedback loop) ──
    try:
        marks_text = ", ".join(body.marks) if body.marks else "no mark"
        episodic.add_event(NarrativeEvent(
            id=f"user_choice_{body.character}_{uuid.uuid4().hex[:12]}",
            chapter=0,
            position="user",
            protagonist=body.character,
            summary=f"User chose option {body.option_label} ({marks_text})",
            importance=0.8,
            zwaan_dims={
                "time": str(episodic.get_max_chapter(body.character) or 0),
                "protagonist": body.character,
                "causality": "user made a choice",
                "intent": marks_text,
            },
        ))
    except Exception:
        pass  # non-blocking

    # ── Save to conversation_history for cross-session persistence ──
    try:
        state = load_session_state(body.character)
        if state:
            last_options = state.get("last_options", [])
            last_question = state.get("last_question", "")
            conv_hist = state.get("conversation_history", [])
            if not isinstance(conv_hist, list):
                conv_hist = []
            
            if last_question and last_options:
                # Map label (A/B/C/D) to index
                labels = ["A", "B", "C", "D", "E"]
                chosen_idx = None
                for i, lbl in enumerate(labels):
                    if lbl == body.option_label.strip().upper():
                        chosen_idx = i
                        break
                
                conv_entry = {
                    "text": last_question,
                    "options": last_options,
                    "chosen": chosen_idx,
                }
                conv_hist.append(conv_entry)
                
                save_session_state(
                    character=body.character,
                    conversation_history=conv_hist,
                )
    except Exception:
        pass  # non-blocking

    return FeedbackResponse(
        status="ok",
        updated=result["updated"],
        preferred_profile=result["profile"],
    )

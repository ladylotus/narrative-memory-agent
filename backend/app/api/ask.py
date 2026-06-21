"""API endpoints — /ask: ask a character."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.database import get_character
from app.models import AskRequest, AskResponse, Option
from app.memory.working import WorkingMemory
from app.services.generation import GenerationService
from app.services.session_resumption import (
    restore_working_memory,
    save_session_state,
)
from app.services.validation import ValidationService

router = APIRouter()
gen = GenerationService()
val = ValidationService()

# Per-character working memory buffers
_sessions: dict[str, WorkingMemory] = {}


def _get_wm(character: str) -> WorkingMemory:
    """Get or create working memory for a character.

    If the character has a saved session state (from a previous session),
    it is automatically restored — this is the core of cross-session memory.
    """
    if character not in _sessions:
        # Checkpoint any previously-active characters before starting a new one
        _checkpoint_all_other(character)

        wm = WorkingMemory()
        # Restore cross-session memory from SQLite
        restored = restore_working_memory(character, wm)
        _sessions[character] = wm

    return _sessions[character]


def _checkpoint_all_other(exclude: str) -> None:
    """Save working memory for all active characters except the one being activated.

    Called when the user switches to a character — ensures the previous
    character's session state is persisted before it falls out of use.
    """
    for other in list(_sessions.keys()):
        if other == exclude:
            continue
        wm = _sessions[other]
        turns = wm.get_context()
        if not turns:
            # Nothing to save — skip
            continue
        char_data = get_character(other)
        preferred = None
        if char_data:
            preferred = char_data.get("preferred_profile")
        save_session_state(
            character=other,
            working_memory=wm,
            preferred_profile=preferred,
        )
        # Clear the in-memory buffer since it's now persisted
        wm.clear()


@router.post("/", response_model=AskResponse)
async def ask_character(body: AskRequest):
    """Ask a character: Circuit A (generation) + Circuit B (validation).

    Injects recent conversation history from WorkingMemory so the
    character remembers previous exchanges within the same session.
    """
    try:
        wm = _get_wm(body.character)

        # Circuit A: generate options with working memory context
        raw_options = await gen.generate_options(
            character=body.character,
            question=body.question,
            num_options=body.num_options,
            context_history=wm.get_context(),
        )

        # Circuit B: validate each option
        scores = await val.validate_many(body.character, raw_options)

        # Merge options with scores
        merged = []
        for i, opt in enumerate(raw_options):
            score = scores[i] if i < len(scores) else {}
            ooc_risk = score.get("ooc_risk", 0.5)
            details = score.get("details", {})

            # Determine risk level tag
            if ooc_risk < 0.33:
                tag = "Low Risk"
                risk_level = "low"
            elif ooc_risk < 0.66:
                tag = "Medium Risk"
                risk_level = "med"
            else:
                tag = "High Risk"
                risk_level = "high"

            merged.append(Option(
                label=opt.get("label", chr(65 + i)),
                description=opt.get("title", ""),
                ooc_risk=ooc_risk,
                ooc_details={
                    "text": opt.get("voice", ""),
                    "level": risk_level,
                    "tag": tag,
                    "type": details.get("type", "normal"),
                    "T": details.get("T"),
                    "B": details.get("B"),
                    "D": details.get("D"),
                    "C": details.get("C"),
                    "P": details.get("P"),
                    "reason": score.get("reason", ""),
                },
            ))

        # Record user question in working memory
        wm.add(role="user", content=body.question)

        # Auto-checkpoint: persist working memory after each interaction
        # so the session survives crashes and server restarts
        char_data = get_character(body.character)
        preferred = None
        if char_data:
            preferred = char_data.get("preferred_profile")
        save_session_state(
            character=body.character,
            working_memory=wm,
            question=body.question,
            preferred_profile=preferred,
        )

        return AskResponse(
            character=body.character,
            question=body.question,
            options=merged,
            status="ok",
        )

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {e}")

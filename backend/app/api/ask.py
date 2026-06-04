"""API endpoints — /ask: ask a character."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.models import AskRequest, AskResponse, Option
from app.services.generation import GenerationService
from app.services.validation import ValidationService

router = APIRouter()
gen = GenerationService()
val = ValidationService()


@router.post("/", response_model=AskResponse)
async def ask_character(body: AskRequest):
    """Ask a character: Circuit A (generation) + Circuit B (validation)."""
    try:
        # Circuit A: generate options
        raw_options = await gen.generate_options(
            character=body.character,
            question=body.question,
            num_options=body.num_options,
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
                tag = "低风险"
                risk_level = "low"
            elif ooc_risk < 0.66:
                tag = "中风险"
                risk_level = "med"
            else:
                tag = "高风险"
                risk_level = "high"

            merged.append(Option(
                label=opt.get("label", chr(65 + i)),
                description=opt.get("title", ""),
                ooc_risk=ooc_risk,
                ooc_details={
                    "text": opt.get("voice", ""),
                    "level": risk_level,
                    "tag": tag,
                    "T": details.get("T"),
                    "B": details.get("B"),
                    "D": details.get("D"),
                    "C": details.get("C"),
                    "P": details.get("P"),
                    "reason": score.get("reason", ""),
                },
            ))

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

"""Pydantic models — request/response schemas."""

from __future__ import annotations

from pydantic import BaseModel, Field


# --- /ask ---

class AskRequest(BaseModel):
    character: str = Field(..., description="Character name")
    question: str = Field(..., description="What to ask the character")
    num_options: int = Field(default=3, ge=2, le=5)


class Option(BaseModel):
    label: str  # e.g. "A", "B", "C"
    description: str
    ooc_risk: float = Field(default=0.0, ge=0.0, le=1.0)
    ooc_details: dict = Field(default_factory=dict)


class AskResponse(BaseModel):
    character: str
    question: str
    options: list[Option]
    status: str = "ok"


# --- /ingest ---

class IngestRequest(BaseModel):
    text: str
    title: str | None = None
    chapter: int | None = None

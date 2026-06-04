"""API endpoints — /ingest: novel ingestion → memory construction."""

from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.ingestion import IngestionService

router = APIRouter()
_service = IngestionService()


class IngestRequest(BaseModel):
    text: str
    title: str | None = None


class IngestResponse(BaseModel):
    status: str
    title: str
    chunks_processed: int
    events_extracted: int
    characters_found: list[str]
    new_characters: list[str]


@router.post("/", response_model=IngestResponse)
async def ingest_text(body: IngestRequest) -> IngestResponse:
    """Ingest novel text → extract events + characters → populate memory layers."""
    result = await _service.process_text(body.text, title=body.title)
    return IngestResponse(**result)


@router.get("/status/{job_id}")
async def ingest_status(job_id: str):
    """Check ingestion job status (placeholder for async)."""
    return {"status": "completed", "job_id": job_id}

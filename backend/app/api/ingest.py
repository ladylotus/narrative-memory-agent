"""API endpoints — /ingest: novel ingestion."""

from __future__ import annotations

from fastapi import APIRouter

router = APIRouter()


@router.post("/")
async def ingest_text():
    """Ingest novel text → character distillation → memory construction."""
    return {"status": "not_implemented", "message": "WIP — /ingest endpoint"}


@router.get("/status/{job_id}")
async def ingest_status(job_id: str):
    """Check ingestion job status."""
    return {"status": "not_implemented", "job_id": job_id}

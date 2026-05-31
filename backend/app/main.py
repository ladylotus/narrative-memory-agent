"""FastAPI application entry point."""

from __future__ import annotations

import uvicorn
from fastapi import FastAPI

from app.api import ask, ingest, profile, sleep

app = FastAPI(
    title="Narrative Memory Agent",
    description="Qwen Cloud Hackathon — Track 1: MemoryAgent",
    version="0.1.0",
)

app.include_router(ingest.router, prefix="/ingest", tags=["ingest"])
app.include_router(ask.router, prefix="/ask", tags=["ask"])
app.include_router(profile.router, prefix="/profile", tags=["profile"])
app.include_router(sleep.router, prefix="/sleep", tags=["sleep"])


@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "project": "narrative-memory-agent"}


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

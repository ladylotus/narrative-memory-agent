"""FastAPI application entry point."""

from __future__ import annotations

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import ask, feedback, ingest, profile, session, sleep
from app.seed import seed_demo_character

app = FastAPI(
    title="Narrative Memory Agent",
    description="Qwen Cloud Hackathon — Track 1: MemoryAgent",
    version="0.1.0",
)

# Allow frontend (localhost:3000) to call backend (localhost:8000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Seed demo data on startup
@app.on_event("startup")
async def startup() -> None:
    seed_demo_character()

app.include_router(ingest.router, prefix="/ingest", tags=["ingest"])
app.include_router(ask.router, prefix="/ask", tags=["ask"])
app.include_router(feedback.router, prefix="/feedback", tags=["feedback"])
app.include_router(profile.router, prefix="/profile", tags=["profile"])
app.include_router(sleep.router, prefix="/sleep", tags=["sleep"])
app.include_router(session.router, prefix="/session", tags=["session"])


@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "project": "narrative-memory-agent"}


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

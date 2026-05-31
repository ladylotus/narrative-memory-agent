"""Ingestion service — novel text → memory construction."""

from __future__ import annotations


class IngestionService:
    """Process novel text through the three memory layers."""

    async def process_text(self, text: str, title: str | None = None) -> dict:
        """Pipeline: tokenize → character detection → event extraction → store."""
        # TODO: Circuit A — LLM extracts events, identifies characters
        # TODO: Store into working → episodic → semantic
        return {
            "status": "not_implemented",
            "characters_found": [],
            "events_extracted": 0,
        }

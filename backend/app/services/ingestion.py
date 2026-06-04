"""Ingestion service — novel text → memory construction pipeline.

Pipeline:
  1. Chunk text into manageable segments
  2. For each chunk, use Qwen to extract events + characters
  3. Build NarrativeEvent objects with Zwaan indexing
  4. Generate embeddings via text-embedding-v3
  5. Store events → EpisodicMemory (SQLite + ChromaDB)
  6. Upsert characters → Database + SemanticMemory
"""

from __future__ import annotations

import json
import re
import uuid
from typing import Any

from openai import AsyncOpenAI

from app.config import QWEN_API_KEY, QWEN_BASE_URL, QWEN_MODEL, QWEN_EMBEDDING_MODEL
from app.database import get_character, upsert_character, list_characters
from app.memory.episodic import EpisodicMemory
from app.memory.vectors import VectorStore
from app.models.event import NarrativeEvent
from app.models.character import CharacterProfile, Trait


# ── Clients ──────────────────────────────────────────────

_client: AsyncOpenAI | None = None


def _get_client() -> AsyncOpenAI:
    global _client
    if _client is None:
        _client = AsyncOpenAI(api_key=QWEN_API_KEY, base_url=QWEN_BASE_URL)
    return _client


# ── IngestionService ─────────────────────────────────────

class IngestionService:
    """Orchestrate novel text ingestion into the three memory layers."""

    def __init__(self) -> None:
        self._episodic = EpisodicMemory()
        self._vectors = VectorStore()

    # ── Public entry point ────────────────────────────────

    async def process_text(
        self,
        text: str,
        title: str | None = None,
        chunk_size: int = 3000,
    ) -> dict[str, Any]:
        """Ingest novel text: extract → embed → store.

        Args:
            text: Full novel text (or chapter excerpt).
            title: Optional chapter/work title for metadata.
            chunk_size: Approximate character count per LLM call.

        Returns:
            Summary dict with counts of events/characters found.
        """
        chunks = self._chunk_text(text, chunk_size)
        all_events: list[NarrativeEvent] = []
        all_characters: dict[str, dict[str, Any]] = {}
        chapter_number = 1  # simplistic — one file = one chapter for now

        for i, chunk in enumerate(chunks):
            result = await self._analyze_chunk(chunk, chapter_number, i + 1)
            events = result.get("events", [])
            characters = result.get("characters", {})

            for evt_data in events:
                event = self._build_event(evt_data, chapter_number, i)
                all_events.append(event)

            for name, info in characters.items():
                if name not in all_characters:
                    all_characters[name] = {"mentions": 0, "traits": [], "relations": {}}
                all_characters[name]["mentions"] += 1
                all_characters[name]["traits"] = self._merge_traits(
                    all_characters[name]["traits"],
                    info.get("traits", []),
                )
                all_characters[name]["relations"].update(info.get("relations", {}))

        # Generate embeddings & store events
        for event in all_events:
            embedding = await self._get_embedding(event.summary)
            if embedding:
                event.embedding = embedding
            self._episodic.add_event(event)

            # Index in ChromaDB
            if embedding:
                self._vectors.add(
                    collection="events",
                    id=event.id,
                    embedding=embedding,
                    metadata={
                        "event_id": event.id,
                        "protagonist": event.protagonist,
                        "chapter": event.chapter,
                        "summary": event.summary[:200],
                    },
                )

        # Upsert characters to database
        new_characters: list[str] = []
        for name, info in all_characters.items():
            existing = get_character(name)
            if not existing:
                new_characters.append(name)
            merged = self._merge_character(existing, name, info)
            upsert_character(merged)

        return {
            "status": "ok",
            "title": title or "",
            "chunks_processed": len(chunks),
            "events_extracted": len(all_events),
            "characters_found": list(all_characters.keys()),
            "new_characters": new_characters,
        }

    # ── Chunking ──────────────────────────────────────────

    @staticmethod
    def _chunk_text(text: str, max_size: int) -> list[str]:
        """Split text on paragraph boundaries, each ≤ max_size chars."""
        if len(text) <= max_size:
            return [text]

        chunks: list[str] = []
        paragraphs = text.split("\n\n")
        current = ""

        for para in paragraphs:
            if len(current) + len(para) + 2 <= max_size:
                current = (current + "\n\n" + para).strip()
            else:
                if current:
                    chunks.append(current)
                # If a single paragraph is too long, split on sentences
                if len(para) > max_size:
                    sentences = re.split(r"(?<=[.!?])\s+", para)
                    sub = ""
                    for sent in sentences:
                        if len(sub) + len(sent) + 1 <= max_size:
                            sub = (sub + " " + sent).strip()
                        else:
                            if sub:
                                chunks.append(sub)
                            sub = sent
                    if sub:
                        chunks.append(sub)
                else:
                    current = para
        if current:
            chunks.append(current)
        return chunks

    # ── LLM analysis ──────────────────────────────────────

    async def _analyze_chunk(
        self,
        chunk: str,
        chapter: int,
        chunk_index: int,
    ) -> dict[str, Any]:
        """Send a chunk to Qwen and parse structured event/character extraction."""
        client = _get_client()

        system_prompt = (
            "You are a literary analysis AI. Your task is to extract structured "
            "narrative information from a novel passage.\n\n"
            "For each passage, identify:\n"
            "1. **Events** — discrete narrative moments. Each event should have:\n"
            "   - A short summary\n"
            "   - The protagonist (whose perspective or action drives this moment)\n"
            "   - Importance (0.0–1.0: how significant to the overall narrative)\n"
            "   - Zwaan dimensions: time (when), space (where), protagonist (who),\n"
            "     causality (what caused this), intent (what the character wants)\n"
            "   - Related entities (other characters or objects involved)\n"
            "2. **Characters** — any named or distinctly referenced characters.\n"
            "   For each: their traits/behaviors shown in this passage, and relations\n"
            "   to other characters.\n\n"
            "Return ONLY valid JSON, no other text, in this exact format:\n"
            '{\n'
            '  "events": [\n'
            '    {\n'
            '      "summary": "Lena saves venison from burning.",\n'
            '      "protagonist": "Lena",\n'
            '      "importance": 0.4,\n'
            '      "zwaan": {\n'
            '        "time": "afternoon, banquet prep day",\n'
            '        "space": "Ashmark Pack kitchen",\n'
            '        "protagonist": "Lena",\n'
            '        "causality": "Theron is yelling, Nell panics",\n'
            '        "intent": "prevent waste, mentor Nell"\n'
            '      },\n'
            '      "related": ["Nell", "Beta Theron"]\n'
            '    }\n'
            '  ],\n'
            '  "characters": {\n'
            '    "Lena": {\n'
            '      "traits": ["calm under pressure", "skilled cook", "protective of other Omegas"],\n'
            '      "relations": {"Nell": "mentors", "Maren": "mentor (deceased)", "Beta Theron": "fears but defers"}\n'
            '    }\n'
            '  }\n'
            '}\n'
        )

        resp = await client.chat.completions.create(
            model=QWEN_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Analyze this passage:\n\n{chunk}"},
            ],
            temperature=0.3,
            max_tokens=4096,
        )

        content = resp.choices[0].message.content or "{}"
        return self._parse_analysis(content)

    @staticmethod
    def _parse_analysis(raw: str) -> dict[str, Any]:
        """Extract structured JSON from LLM response."""
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if not match:
            return {"events": [], "characters": {}}
        try:
            data = json.loads(match.group())
        except json.JSONDecodeError:
            return {"events": [], "characters": {}}
        return {
            "events": data.get("events", []),
            "characters": data.get("characters", {}),
        }

    # ── Event building ────────────────────────────────────

    @staticmethod
    def _build_event(
        data: dict[str, Any],
        chapter: int,
        chunk_index: int,
    ) -> NarrativeEvent:
        """Convert extracted event dict to NarrativeEvent dataclass."""
        zwaan = data.get("zwaan", {})
        if isinstance(zwaan, dict):
            # Ensure all 5 Zwaan keys exist
            for key in ("time", "space", "protagonist", "causality", "intent"):
                zwaan.setdefault(key, "unknown")
        else:
            zwaan = {"time": "unknown", "space": "unknown", "protagonist": data.get("protagonist", "unknown"),
                     "causality": "unknown", "intent": "unknown"}

        return NarrativeEvent(
            id=f"evt_{uuid.uuid4().hex[:10]}",
            chapter=chapter,
            position=f"{chunk_index + 1}/?",
            protagonist=data.get("protagonist", "unknown"),
            summary=data.get("summary", ""),
            importance=min(max(float(data.get("importance", 0.5)), 0.0), 1.0),
            embedding=None,  # filled later
            related_entities=data.get("related", []),
            zwaan_dims=zwaan,
        )

    # ── Embedding ──────────────────────────────────────────

    async def _get_embedding(self, text: str) -> list[float] | None:
        """Generate embedding via Qwen's text-embedding-v3."""
        client = _get_client()
        try:
            resp = await client.embeddings.create(
                model=QWEN_EMBEDDING_MODEL,
                input=text,
            )
            return resp.data[0].embedding
        except Exception:
            return None

    # ── Character merging ──────────────────────────────────

    @staticmethod
    def _merge_traits(
        existing: list[dict[str, Any]],
        new_raw: list[str | dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Combine existing structured traits with new extractions.

        Handles both string lists and dict lists from LLM output.
        """
        existing_names = {t.get("name", "") for t in existing}
        for item in new_raw:
            # Normalise: handle both string and dict formats
            if isinstance(item, dict):
                name = item.get("name", "")
                if name and name not in existing_names:
                    existing.append({
                        "name": name,
                        "category": item.get("category", "surface"),
                        "description": item.get("description", ""),
                        "confidence": float(item.get("confidence", 0.3)),
                    })
                    existing_names.add(name)
            elif isinstance(item, str) and item not in existing_names:
                existing.append({
                    "name": item,
                    "category": "surface",
                    "description": "",
                    "confidence": 0.3,
                })
                existing_names.add(item)
        return existing

    @staticmethod
    def _merge_character(
        existing: dict[str, Any] | None,
        name: str,
        info: dict[str, Any],
    ) -> dict[str, Any]:
        """Merge LLM extraction with existing character data."""
        base = {
            "name": name,
            "aliases": [],
            "traits": [],
            "relations": {},
            "motivation": "",
            "arc_stage": "unknown",
            "backstory": "",
            "embedding_centroid": None,
            "preferred_profile": None,
        }
        if existing:
            base.update(existing)

        # Merge traits
        new_traits = info.get("traits", [])
        base["traits"] = IngestionService._merge_traits(
            base.get("traits", []),
            new_traits,
        )

        # Merge relations
        new_relations = info.get("relations", {})
        existing_relations = base.get("relations", {})
        for rel_name, rel_desc in new_relations.items():
            if rel_name not in existing_relations:
                existing_relations[rel_name] = rel_desc
        base["relations"] = existing_relations

        return base

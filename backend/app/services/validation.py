"""Circuit B — OOC validation using multi-factor scoring via Qwen + real vector distance.

Implements: OOC_Risk = 1 - (αT + βB + γ(1-D) + δC - εP)

Semantic distance (D) is computed from real ChromaDB embedding distance,
not estimated by the LLM.
"""

from __future__ import annotations

import json
import re
import statistics
from typing import Any

from openai import AsyncOpenAI

from app.config import QWEN_API_KEY, QWEN_BASE_URL, QWEN_MODEL, QWEN_EMBEDDING_MODEL
from app.database import get_character
from app.memory.vectors import VectorStore


_client: AsyncOpenAI | None = None


def _get_client() -> AsyncOpenAI:
    global _client
    if _client is None:
        _client = AsyncOpenAI(
            api_key=QWEN_API_KEY,
            base_url=QWEN_BASE_URL,
            timeout=120.0,
        )
    return _client


class ValidationService:
    """Validate character responses against established cognitive profile.

    Uses a multi-factor model:
      α (trait consistency)  — 0.35  — does it violate core traits?
      β (behaviour pattern)  — 0.25  — is it consistent with past behaviour?
      γ (semantic distance)  — 0.15  — is it semantically far from the character's
                              historical events? (computed from real ChromaDB vectors)
      δ (self-consistency)   — 0.15  — is the option internally consistent?
      ε (novelty / surprise) — 0.10  — is it unexpectedly but plausibly interesting?
    """

    def __init__(self) -> None:
        self.alpha = 0.35
        self.beta = 0.25
        self.gamma = 0.15
        self.delta = 0.15
        self.epsilon = 0.10
        self._vectors = VectorStore()

    # ── public ───────────────────────────────────

    async def validate_many(
        self,
        character: str,
        options: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Score all options against the character's profile in one Qwen call.

        The LLM evaluates T (trait), B (behaviour), C (self-consistency),
        and P (surprise).  Semantic distance D is computed separately from
        real ChromaDB embeddings so it reflects actual narrative history
        rather than the LLM's self-estimate.
        """
        profile = get_character(character)
        if profile is None:
            raise ValueError(f"Character '{character}' not found")

        traits = profile.get("traits", [])
        trait_desc = "; ".join(
            f"{t.get('name', '?')} ({t.get('category', '?')}): {t.get('description', '')}"
            for t in traits
        )

        options_text = "\n\n".join(
            f"Option {opt.get('label', chr(65 + i))}: \"{opt.get('voice', '')}\""
            for i, opt in enumerate(options)
        )

        # ── LLM prompt — evaluates T, B, C, P (NOT D) ──────────
        prompt = (
            f"You are an OOC (Out-of-Character) evaluation assistant for a novel.\n\n"
            f"Character: {profile['name']}\n"
            f"Backstory: {profile.get('backstory', '')}\n"
            f"Core traits: {trait_desc}\n"
            f"Motivation: {profile.get('motivation', '')}\n\n"
            f"Below are response options generated for this character.\n"
            f"For EACH option, rate the following **four** dimensions on a scale "
            f"of 0.0 to 1.0:\n\n"
            f"- T (Trait consistency): Does this option violate any core trait? "
            f"1.0 = perfectly consistent, 0.0 = violates a core trait.\n"
            f"- B (Behaviour consistency): Is this consistent with how the character "
            f"would behave based on their past? 1.0 = very consistent, 0.0 = never.\n"
            f"- C (Self-consistency): Is this option internally logical and "
            f"non-contradictory? 1.0 = perfectly self-consistent, 0.0 = contradictory.\n"
            f"- P (Surprise / novelty): How unexpected is this option? "
            f"1.0 = very surprising but still plausible, 0.0 = totally predictable.\n\n"
            f"Options to evaluate:\n{options_text}\n\n"
            f"Return ONLY valid JSON, no other text:\n"
            f'{{"scores": [\n'
            f'  {{"label": "A", "T": 0.9, "B": 0.8, "C": 0.9, "P": 0.1, '
            f'"reason": "brief note"}},\n'
            f"  ...\n"
            f"]}}\n"
        )

        client = _get_client()
        resp = await client.chat.completions.create(
            model=QWEN_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=2048,
            timeout=90,
        )

        content = resp.choices[0].message.content or "{}"
        raw_scores = self._parse_scores(content, len(options))

        # ── Compute real semantic distance D from ChromaDB ──────
        real_d_values = await self._compute_semantic_distances(options, character)

        # ── Apply formula to each option ────────────────────────
        for i, score in enumerate(raw_scores):
            t = score.get("T", 0.5)
            b = score.get("B", 0.5)
            # Use REAL semantic distance instead of LLM estimate
            d = real_d_values[i] if i < len(real_d_values) else 0.5
            c = score.get("C", 0.5)
            p = score.get("P", 0.5)

            risk = 1.0 - (
                self.alpha * t
                + self.beta * b
                + self.gamma * (1.0 - d)
                + self.delta * c
                - self.epsilon * p
            )
            # Clamp to [0, 1]
            risk = max(0.0, min(1.0, risk))

            score["ooc_risk"] = round(risk, 4)
            score["details"] = {
                "T": round(t, 2),
                "B": round(b, 2),
                # D is now real vector distance, tagged so consumers can distinguish
                "D": round(d, 2),
                "C": round(c, 2),
                "P": round(p, 2),
                "D_source": "chromadb",
            }

            # Classify: violation (low T/B/C) vs surprise (high P, OK consistency)
            consistency = (t + b + c) / 3.0
            if risk >= 0.66 and consistency < 0.4:
                score["details"]["type"] = "violation"
            elif risk >= 0.66 and p >= 0.6 and consistency >= 0.4:
                score["details"]["type"] = "surprise"
            else:
                score["details"]["type"] = "normal"

        return raw_scores

    # ── ChromaDB semantic distance ───────────────

    async def _compute_semantic_distances(
        self,
        options: list[dict[str, Any]],
        character: str,
    ) -> list[float]:
        """Compute real semantic distance D for each option against character's historical events.

        For each option:
          1. Generate embedding via text-embedding-v3
          2. Query ChromaDB 'events' collection filtered by protagonist
          3. Average the L2 distances across top results
          4. Normalise to [0, 1] semantic distance

        Returns a list of D values in [0, 1], one per option.
        """
        client = _get_client()
        d_values: list[float] = []

        for opt in options:
            voice = opt.get("voice", "")
            if not voice:
                d_values.append(0.5)
                continue

            # Step 1: get embedding for this option
            try:
                emb_resp = await client.embeddings.create(
                    model=QWEN_EMBEDDING_MODEL,
                    input=voice,
                    timeout=30,
                )
                embedding = emb_resp.data[0].embedding
            except Exception:
                d_values.append(0.5)
                continue

            # Step 2: search ChromaDB for character's events
            try:
                results = self._vectors.search(
                    collection="events",
                    query_embedding=embedding,
                    top_k=10,
                    where={"protagonist": character},
                )
            except Exception:
                d_values.append(0.5)
                continue

            # Step 3: compute average L2 distance
            if not results:
                d_values.append(0.5)
                continue

            distances = [
                r["score"] for r in results if r["score"] is not None
            ]
            if not distances:
                d_values.append(0.5)
                continue

            avg_dist = statistics.mean(distances)

            # Step 4: normalise L2 → [0, 1] semantic distance
            # text-embedding-v3 produces near-unit-normalised vectors.
            # L2 range: 0 (identical) → ~2 (opposite for unit vectors).
            # Map to D where 0 = same semantic space, 1 = very far.
            # Cap at 1.0 for safety; floor at 0.0.
            d = max(0.0, min(1.0, avg_dist / 1.5))
            d_values.append(round(d, 4))

        return d_values

    # ── helpers ──────────────────────────────────

    @staticmethod
    def _parse_scores(raw: str, expected_count: int) -> list[dict[str, Any]]:
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if not match:
            return _fallback_scores(expected_count)

        try:
            data = json.loads(match.group())
        except json.JSONDecodeError:
            return _fallback_scores(expected_count)

        scores = data.get("scores", [])
        if not scores:
            return _fallback_scores(expected_count)
        return scores


def _fallback_scores(count: int) -> list[dict[str, Any]]:
    """Neutral fallback when parsing fails."""
    return [
        {
            "label": chr(65 + i),
            "T": 0.5,
            "B": 0.5,
            "C": 0.5,
            "P": 0.0,
            "ooc_risk": 0.5,
            "reason": "fallback — unable to parse LLM response",
            "details": {"T": 0.5, "B": 0.5, "D": 0.5, "C": 0.5, "P": 0.0, "D_source": "fallback", "type": "normal"},
        }
        for i in range(count)
    ]

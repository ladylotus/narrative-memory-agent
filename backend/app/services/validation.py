"""Circuit B — OOC validation using multi-factor scoring via Qwen.

Implements: OOC_Risk = 1 - (αT + βB + γ(1-D) + δC - εP)
"""

from __future__ import annotations

import json
import re
from typing import Any

from openai import AsyncOpenAI

from app.config import QWEN_API_KEY, QWEN_BASE_URL, QWEN_MODEL
from app.database import get_character


_client: AsyncOpenAI | None = None


def _get_client() -> AsyncOpenAI:
    global _client
    if _client is None:
        _client = AsyncOpenAI(api_key=QWEN_API_KEY, base_url=QWEN_BASE_URL)
    return _client


class ValidationService:
    """Validate character responses against established cognitive profile.

    Uses a multi-factor model:
      α (trait consistency)  — 0.35  — does it violate core traits?
      β (behaviour pattern)  — 0.25  — is it consistent with past behaviour?
      γ (semantic distance)  — 0.15  — is it semantically far from the character's centroid?
      δ (self-consistency)   — 0.15  — is the option internally consistent?
      ε (novelty / surprise) — 0.10  — is it unexpectedly but plausibly interesting?
    """

    def __init__(self) -> None:
        self.alpha = 0.35
        self.beta = 0.25
        self.gamma = 0.15
        self.delta = 0.15
        self.epsilon = 0.10

    async def validate_many(
        self,
        character: str,
        options: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Score all options against the character's profile in one Qwen call."""
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

        prompt = (
            f"You are an OOC (Out-of-Character) evaluation assistant for a novel.\n\n"
            f"Character: {profile['name']}\n"
            f"Backstory: {profile.get('backstory', '')}\n"
            f"Core traits: {trait_desc}\n"
            f"Motivation: {profile.get('motivation', '')}\n\n"
            f"Below are response options generated for this character.\n"
            f"For EACH option, rate the following five dimensions on a scale of 0.0 to 1.0:\n\n"
            f"- T (Trait consistency): Does this option violate any core trait? "
            f"1.0 = perfectly consistent, 0.0 = violates a core trait.\n"
            f"- B (Behaviour consistency): Is this consistent with how the character "
            f"would behave based on their past? 1.0 = very consistent, 0.0 = never.\n"
            f"- D (Semantic distance): How far is this option from the character's "
            f"usual 'voice' conceptually? 1.0 = very far, 0.0 = exactly their usual space.\n"
            f"- C (Self-consistency): Is this option internally logical and non-contradictory? "
            f"1.0 = perfectly self-consistent, 0.0 = contradictory.\n"
            f"- P (Surprise / novelty): How unexpected is this option? "
            f"1.0 = very surprising but still plausible, 0.0 = totally predictable.\n\n"
            f"Options to evaluate:\n{options_text}\n\n"
            f"Return ONLY valid JSON, no other text:\n"
            f'{{"scores": [\n'
            f'  {{"label": "A", "T": 0.9, "B": 0.8, "D": 0.2, "C": 0.9, "P": 0.1, "reason": "brief note"}},\n'
            f"  ...\n"
            f"]}}\n"
        )

        client = _get_client()
        resp = await client.chat.completions.create(
            model=QWEN_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=2048,
        )

        content = resp.choices[0].message.content or "{}"
        raw_scores = self._parse_scores(content, len(options))

        # Apply formula to each option
        for score in raw_scores:
            t = score.get("T", 0.5)
            b = score.get("B", 0.5)
            d = score.get("D", 0.5)
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
                "D": round(d, 2),
                "C": round(c, 2),
                "P": round(p, 2),
            }

        return raw_scores

    # ── helpers ────────────────────────────────

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
            "D": 0.5,
            "C": 0.5,
            "P": 0.0,
            "ooc_risk": 0.5,
            "reason": "fallback — unable to parse LLM response",
            "details": {"T": 0.5, "B": 0.5, "D": 0.5, "C": 0.5, "P": 0.0},
        }
        for i in range(count)
    ]

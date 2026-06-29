"""Circuit A — creative generation (character voice) using Qwen API."""

from __future__ import annotations

import json
import re
from typing import Any

from openai import AsyncOpenAI

from app.config import QWEN_API_KEY, QWEN_BASE_URL, QWEN_MODEL
from app.database import get_character
from app.memory.working import Turn
from app.services.bias_prompt import profile_to_bias_prompt


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


# ──────────────────────────────────────────────
#  GenerationService
# ──────────────────────────────────────────────

class GenerationService:
    """Generate character response options in role — Circuit A.

    Reads the character profile from the database, builds a role-playing
    prompt, and asks Qwen to produce ``num_options`` differentiated
    development paths. Each option carries a brief description of its
    "track" (safe / interesting / bold).

    When ``context_history`` is provided (from WorkingMemory), previous
    conversation turns are injected so the character acts with awareness
    of what has already been discussed.
    """

    async def generate_options(
        self,
        character: str,
        question: str,
        num_options: int = 4,
        context_history: list[Turn] | None = None,
        episodic_context: dict[str, list[dict[str, Any]]] | None = None,
    ) -> list[dict[str, Any]]:
        profile = get_character(character)
        if profile is None:
            raise ValueError(f"Character '{character}' not found in database")

        traits = profile.get("traits", [])
        trait_desc = "; ".join(
            f"{t.get('name', '?')} ({t.get('category', 'core')}): "
            f"{t.get('description', '')}"
            for t in traits
        )

        # ── System prompt (always present) ──────────────────────
        system_prompt = (
            f"You are {profile['name']}.\n"
            f"Backstory: {profile.get('backstory', '')}\n"
            f"Core traits: {trait_desc}\n"
            f"Motivation: {profile.get('motivation', '')}\n"
            f"Current arc stage: {profile.get('arc_stage', 'unknown')}\n"
            f"\n"
            f"You are a character in a novel. A reader/author asks you a question "
            f"about what you would do in a given situation.\n"
            f"Answer **in first person**, in your own voice and style.\n"
            f"Speak naturally — you don't have to explain yourself.\n"
            f"You can be uncertain, decisive, conflicted, or mysterious — "
            f"whatever fits.\n"
        )

        # ── Conversation history from WorkingMemory ─────────────
        if context_history:
            turns_text = "\n".join(
                f"{'Reader' if t.role == 'user' else 'You'}: {t.content}"
                for t in context_history
            )
            system_prompt += (
                f"\n"
                f"Conversation so far:\n"
                f"{turns_text}\n"
            )

        # ── Generation Bias: preferred_profile ──────────────────
        preferred = profile.get("preferred_profile")
        if preferred and isinstance(preferred, list) and len(preferred) >= 5:
            bias_text = profile_to_bias_prompt(preferred)
            if bias_text:
                system_prompt += (
                    f"\n"
                    f"---\n"
                    f"{bias_text}\n"
                    f"---\n"
                )

        # ── Episodic memory context ─────────────────────────────
        if episodic_context:
            active_events = episodic_context.get("active", [])
            fading_events = episodic_context.get("fading", [])
            memory_parts: list[str] = []
            for ev in active_events:
                summary = ev.get("summary", "").strip()
                if summary:
                    memory_parts.append(f"- {summary}")
            for ev in fading_events:
                summary = ev.get("summary", "").strip()
                if summary:
                    memory_parts.append(f"- (vaguely) {summary}")
            if memory_parts:
                system_prompt += (
                    f"\n"
                    f"Things you remember:\n"
                    f"{chr(10).join(memory_parts)}\n"
                )

        # ── User prompt ─────────────────────────────────────────
        user_prompt = (
            f"The reader now asks you: \"{question}\"\n\n"
            f"Give me {num_options} different possible responses you might give.\n"
            f"They MUST represent a **spectrum** of directions — for example:\n"
            f"- One that stays closest to your core nature (safe/expected)\n"
            f"- One that explores a less obvious side of you (interesting/surprising)\n"
            f"- One that is bold or unexpected, pushing the boundary of plausibility\n"
            f"- One that clearly violates your core traits — something you would "
            f"NEVER say or do (out-of-character)\n"
            f"\n"
            f"Return ONLY valid JSON in this exact format, no other text:\n"
            f'{{"options": [\n'
            f'  {{"label": "A", "title": "short title", '
            f'"voice": "the full response in first person"}},\n'
            f'  {{"label": "B", "title": "short title", '
            f'"voice": "the full response in first person"}},\n'
            f'  ...\n'
            f"]}}\n"
        )

        client = _get_client()
        resp = await client.chat.completions.create(
            model=QWEN_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.8,
            max_tokens=2048,
            timeout=90,
        )

        content = resp.choices[0].message.content or "{}"
        return self._parse_options(content)

    # ── helpers ────────────────────────────────

    @staticmethod
    def _parse_options(raw: str) -> list[dict[str, Any]]:
        """Extract the JSON from the LLM response (handles wrapping)."""
        # Try to find a JSON block
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if not match:
            return _fallback_options(raw)

        try:
            data = json.loads(match.group())
        except json.JSONDecodeError:
            return _fallback_options(raw)

        options = data.get("options", [])
        if not options:
            return _fallback_options(raw)

        # Normalise keys & apply defaults
        out = []
        for i, opt in enumerate(options):
            out.append({
                "label": opt.get("label", chr(65 + i)),
                "title": opt.get("title", f"Option {chr(65 + i)}"),
                "voice": opt.get("voice", opt.get("text", "")),
            })
        return out


def _fallback_options(raw: str) -> list[dict[str, Any]]:
    """Last resort — wrap the raw response as a single option."""
    return [
        {
            "label": "A",
            "title": "Response",
            "voice": raw[:500],
        },
    ]

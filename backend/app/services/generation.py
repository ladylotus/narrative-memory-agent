"""Circuit A — creative generation (character voice)."""

from __future__ import annotations


class GenerationService:
    """Generate character responses in role — Circuit A.

    Uses Qwen API to produce multi-option character responses.
    """

    async def generate_options(
        self,
        character: str,
        question: str,
        num_options: int = 3,
    ) -> list[dict]:
        """Generate {num_options} development options in character's voice."""
        # TODO: query semantic memory for character profile
        # TODO: call Qwen with role prompt → generate N options
        return [
            {"label": "A", "description": "Not implemented", "ooc_risk": 0.0},
        ]

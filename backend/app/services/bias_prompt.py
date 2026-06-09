"""Convert preferred_profile (5-dim vector) into natural language bias prompt.

T/B/D/C/P dimensions:
  T — Trait Consistency: how much to adhere to core traits
  B — Behavioral Consistency: how much to follow past behavior patterns
  D — Semantic Distance: how far language can deviate from character norm
  C — Self-Consistency: how internally consistent the response should be
  P — Surprise Factor: how unexpected/surprising the response can be
"""

from __future__ import annotations


def _describe(label: str, value: float, high_desc: str, low_desc: str) -> str:
    """Describe a dimension value in natural language, thresholded."""
    if value >= 0.7:
        level = "strongly"
        desc = high_desc
    elif value >= 0.4:
        level = "moderately"
        desc = high_desc if value >= 0.55 else low_desc
    else:
        level = "slightly"
        desc = low_desc
    return f"{label} ({level} {desc})"


def profile_to_bias_prompt(preferred: list[float]) -> str:
    """Convert a 5-dim preferred_profile into a natural language bias prompt.

    Args:
        preferred: List of 5 floats [T, B, D, C, P] in [0, 1].

    Returns:
        A paragraph describing the user's preference, to inject into system prompt.
    """
    if not preferred or len(preferred) < 5:
        return ""

    t, b, d, c, p = preferred[:5]

    parts = [
        "Based on your previous responses that the reader found most fitting:",
    ]

    # T — Trait Consistency
    if t >= 0.7:
        parts.append("you should stay very close to your core traits and not contradict them.")
    elif t >= 0.4:
        parts.append("you can bend your traits slightly but don't break your core nature.")
    else:
        parts.append("the reader is open to you showing sides that may seem out of character.")

    # B — Behavioral Consistency
    if b >= 0.7:
        parts.append("Follow patterns from your past behaviour — the reader expects consistency.")
    elif b >= 0.4:
        parts.append("You can occasionally break past patterns, but keep recognisable.")
    else:
        parts.append("The reader enjoys when you break away from your usual patterns.")

    # D — Semantic Distance (lower = closer to character voice)
    if d <= 0.3:
        parts.append("Stay close to your usual way of speaking and thinking.")
    elif d <= 0.6:
        parts.append("You can shift your tone a little, but don't sound like a different person.")
    else:
        parts.append("The reader is open to you sounding quite different from your usual self.")

    # C — Self-Consistency
    if c >= 0.7:
        parts.append("Keep your responses internally consistent and coherent.")
    elif c >= 0.4:
        parts.append("A little contradiction is fine if it feels natural.")
    else:
        parts.append("The reader is fine with uncertainty and internal conflict in your responses.")

    # P — Surprise Factor
    if p >= 0.7:
        parts.append("The reader enjoys when you surprise them — bold or unexpected directions are welcome.")
    elif p >= 0.4:
        parts.append("Balanced — safe when the situation calls for it, surprising when it fits.")
    else:
        parts.append("The reader prefers safe, expected directions — don't stray too far.")

    return " ".join(parts)

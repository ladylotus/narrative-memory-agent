"""Generation Bias — EMA computation for preferred_profile.

EMA (Exponential Moving Average) updates the character's preferred_profile,
a 5-dim vector [T, B, D, C, P], based on which options the user marks as
fitting the character.

Decision logic (from 方案文档.md §九, 2026/6/9 复盘):
  - marks contains "角色驱动"      → alpha=0.3  (正常更新)
  - marks only "剧情驱动/实验心态"  → 不更新
  - marks only "说不上来"          → alpha=0.1  (低权重)
  - marks empty (auto mode)        → alpha=0.15 (静默)
"""

from __future__ import annotations

from typing import Any

__all__ = ["update_preferred_profile"]

# ── Constants ──────────────────────────────────────────

DIMENSION_KEYS = ["T", "B", "D", "C", "P"]

ALPHA_CHARACTER_DRIVEN = 0.30   # "这就是他会做的事"
ALPHA_GUT_FEELING = 0.10        # "说不上来，就是感觉"
ALPHA_AUTO = 0.15               # 默认自动（不弹窗，静默更新）
ALPHA_NONE = 0.0                # 剧情驱动/实验心态（不更新）

MARK_CHARACTER_DRIVEN = "这就是他会做的事"
MARK_PLOT_DRIVEN = "情节需要这个走向"
MARK_EXPERIMENTAL = "想看看这个可能性"
MARK_GUT_FEELING = "说不上来，就是感觉"

# ── Logic ──────────────────────────────────────────────


def _should_update(marks: list[str]) -> bool:
    """Should preferred_profile be updated based on marks?"""
    if not marks:
        return True  # auto mode
    if MARK_CHARACTER_DRIVEN in marks:
        return True
    if marks == [MARK_GUT_FEELING]:
        return True
    return False


def _get_alpha(marks: list[str]) -> float:
    """Determine EMA alpha from marks."""
    if not marks:
        return ALPHA_AUTO
    if MARK_CHARACTER_DRIVEN in marks:
        return ALPHA_CHARACTER_DRIVEN
    if marks == [MARK_GUT_FEELING]:
        return ALPHA_GUT_FEELING
    return ALPHA_NONE


def _ema(old: list[float] | None, new: list[float], alpha: float) -> list[float]:
    """Exponential Moving Average — per-dimension."""
    if old is None or len(old) != len(new):
        return new
    return [alpha * n + (1.0 - alpha) * o for o, n in zip(old, new)]


def _scores_to_vector(scores: dict[str, float]) -> list[float]:
    """Extract 5-dim vector from scores dict, defaulting to 0.5."""
    return [scores.get(k, 0.5) for k in DIMENSION_KEYS]


def update_preferred_profile(
    old_profile: list[float] | None,
    selected_scores: dict[str, float],
    marks: list[str],
) -> dict[str, Any]:
    """Update preferred_profile via EMA.

    Args:
        old_profile: Current preferred_profile (list of 5 floats) or None.
        selected_scores: Dict with keys T/B/D/C/P, values in [0, 1].
        marks: User's mark selections (list of strings from the four options).

    Returns:
        {"updated": bool, "profile": list[float] | None}
    """
    if not _should_update(marks):
        return {"updated": False, "profile": old_profile}

    alpha = _get_alpha(marks)
    new_vector = _scores_to_vector(selected_scores)
    updated = _ema(old_profile, new_vector, alpha)

    return {"updated": True, "profile": updated}

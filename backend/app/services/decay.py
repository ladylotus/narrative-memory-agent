"""Decay service — time-based memory decay for episodic events.

Computes a recall_score for each event based on how much time has passed
since it occurred. Events with high recall_scores stay in the active set;
low-scoring events get archived during Sleep consolidation.
"""

from __future__ import annotations

from typing import Any

# ── Config ──────────────────────────────────────────────

# Time decay factor: recall_score = importance × exp(-λ × chapters_elapsed)
# λ = 0.01 means ~1% decay per chapter — conservative, won't affect demos
_LAMBDA_TIME = 0.01

# Classification thresholds
_THRESHOLD_ACTIVE = 0.15   # ≥ : full summary in prompt
_THRESHOLD_ARCHIVE = 0.05  # <  : eligible for archiving
# Between the two → fading: truncated summary in prompt


# ── Public API ──────────────────────────────────────────


def recall_score(
    importance: float,
    chapters_elapsed: int,
) -> float:
    """Compute how recallable an event is, given how many chapters have passed.

    Args:
        importance: The event's narrative importance (0.0 — 1.0).
        chapters_elapsed: Number of chapters since this event occurred
                          (>= 0). Calculated as current_chapter - event_chapter.

    Returns:
        A float in (0.0, importance], decaying over time.
    """
    if importance <= 0.0:
        return 0.0
    if chapters_elapsed < 0:
        chapters_elapsed = 0
    return importance * _exp_neg(_LAMBDA_TIME * chapters_elapsed)


def classify(score: float) -> str:
    """Classify an event based on its recall_score.

    Returns:
        One of "active", "fading", or "archived".
    """
    if score >= _THRESHOLD_ACTIVE:
        return "active"
    if score >= _THRESHOLD_ARCHIVE:
        return "fading"
    return "archived"


def select_context(
    events: list[dict[str, Any]],
    current_chapter: int,
    max_active: int = 10,
    max_fading: int = 5,
) -> dict[str, list[dict[str, Any]]]:
    """Filter and rank events by recall_score for use in a generation prompt.

    Args:
        events: List of event dicts, each with at least "id", "importance",
                "chapter", and "summary".
        current_chapter: The current narrative chapter.
        max_active: Max number of active events to include.
        max_fading: Max number of fading events (truncated) to include.

    Returns:
        {
            "active": [...],   # full-summary events for prompt
            "fading": [...],   # truncated-summary events
            "all_ids": [...],  # all returned event IDs (for access counting)
        }
    """
    scored: list[tuple[float, dict[str, Any]]] = []
    for ev in events:
        chapter = ev.get("chapter", 1) or 1
        imp = ev.get("importance", 0.5) or 0.5
        score = recall_score(imp, current_chapter - chapter)
        scored.append((score, ev))

    # Sort descending by recall_score
    scored.sort(key=lambda x: x[0], reverse=True)

    active: list[dict[str, Any]] = []
    fading: list[dict[str, Any]] = []
    all_ids: list[str] = []

    for score, ev in scored:
        cls = classify(score)
        if cls == "active" and len(active) < max_active:
            active.append(ev)
            all_ids.append(ev.get("id", ""))
        elif cls == "fading" and len(fading) < max_fading:
            # Truncate summary
            ev = dict(ev)
            summary = ev.get("summary", "")
            if len(summary) > 100:
                ev["summary"] = summary[:100] + "…"
            fading.append(ev)
            all_ids.append(ev.get("id", ""))
        elif cls == "archived":
            # Archived events don't enter the prompt at all
            pass
        # Fallthrough for active/fading at capacity — drop

    return {
        "active": active,
        "fading": fading,
        "all_ids": all_ids,
    }


# ── Internal helpers ────────────────────────────────────


def _exp_neg(x: float) -> float:
    """Compute exp(-x) without importing math at module scope.

    Keeps this module dependency-free for easy unit testing.
    """
    # Taylor series for small x; fallback to math for large x
    if x < 0.01:
        return 1.0 - x + (x * x) / 2.0
    # For larger values, import math lazily
    import math
    return math.exp(-x)

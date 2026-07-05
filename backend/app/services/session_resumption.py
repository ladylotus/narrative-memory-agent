"""Session Resumption — serialize/deserialize working memory across sessions.

Core mechanism (from NirDiamant Agent Memory Bible):
  Session 1: user talks to character → on switch/close, serialize WM to SQLite
  Session 2: user returns to character → deserialize WM from SQLite → resume

This implements the "边界操作" (boundary operations) pattern:
  - save_session_state()  at character switch / session close
  - load_session_state()  at character open / session start
"""

from __future__ import annotations
from typing import Any

from app.database import (
    delete_session_state,
    get_session_state,
    upsert_session_state,
)
from app.memory.working import WorkingMemory

__all__ = [
    "save_session_state",
    "load_session_state",
    "checkpoint_working_memory",
    "clear_session_state",
]


def save_session_state(
    character: str,
    working_memory: WorkingMemory | None = None,
    question: str | None = None,
    options_json: list[dict[str, Any]] | None = None,
    conversation_history: list[dict[str, Any]] | None = None,
    preferred_profile: list[float] | None = None,
) -> None:
    """Serialize working memory → SQLite for cross-session persistence.

    Called automatically when switching characters or before sleep.
    If working_memory is None, only the question/preferred_profile are saved.
    """
    # Partial saves must not destroy existing state: any field the caller
    # does not provide is preserved from the stored row (previously, a
    # feedback-path save wiped turns/last_question, producing the
    # contradictory "0 previous exchanges remembered" resumption banner).
    existing: dict[str, Any] = {}
    if (working_memory is None or question is None or options_json is None
            or preferred_profile is None):
        existing = load_session_state(character) or {}

    if working_memory is not None:
        turns = [
            {"role": t.role, "content": t.content}
            for t in working_memory.get_context()
        ]
    else:
        turns = existing.get("turns") or []

    data: dict[str, Any] = {
        "character": character,
        "turns": turns,
        "last_question": question if question is not None else existing.get("last_question", ""),
    }
    data["last_options"] = options_json if options_json is not None else existing.get("last_options")
    if conversation_history is not None:
        data["conversation_history"] = conversation_history
    data["preferred_profile"] = (preferred_profile if preferred_profile is not None
                                 else existing.get("preferred_profile"))

    upsert_session_state(data)


def load_session_state(character: str) -> dict[str, Any] | None:
    """Deserialize working memory from SQLite.

    Returns:
        {
            "character": str,
            "turns": list[{"role": str, "content": str}],
            "last_question": str,
            "last_options": list[dict] | None,
            "preferred_profile": list[float] | None,
        } | None
    """
    return get_session_state(character)


def restore_working_memory(
    character: str,
    working_memory: WorkingMemory,
) -> bool:
    """Load saved session state into an in-memory WorkingMemory buffer.

    Returns True if state was restored, False if no saved state.
    """
    state = load_session_state(character)
    if state is None:
        return False

    turns = state.get("turns", [])
    if turns:
        for turn in turns:
            working_memory.add(
                role=turn.get("role", "user"),
                content=turn.get("content", ""),
            )
    return True


def clear_session_state(character: str) -> None:
    """Remove saved session state (e.g. after sleep consolidation)."""
    delete_session_state(character)

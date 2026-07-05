"""Database layer — SQLite connection + character store."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from app.config import SQLITE_PATH


# ──────────────────────────────────────────────
#  Connection
# ──────────────────────────────────────────────

_conn: sqlite3.Connection | None = None


def get_conn() -> sqlite3.Connection:
    """Get or create the shared SQLite connection."""
    global _conn
    if _conn is None:
        _conn = sqlite3.connect(str(SQLITE_PATH), check_same_thread=False)
        _conn.row_factory = sqlite3.Row
        _init_db(_conn)
    return _conn


def _init_db(conn: sqlite3.Connection) -> None:
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS characters (
            name        TEXT PRIMARY KEY,
            aliases     TEXT NOT NULL DEFAULT '[]',
            traits      TEXT NOT NULL DEFAULT '[]',   -- JSON list of Trait dicts
            relations   TEXT NOT NULL DEFAULT '{}',
            motivation  TEXT NOT NULL DEFAULT '',
            arc_stage   TEXT NOT NULL DEFAULT 'unknown',
            backstory   TEXT NOT NULL DEFAULT '',
            embedding_centroid TEXT,                  -- JSON float array
            preferred_profile  TEXT,                  -- JSON [T,B,D,C,P] for Generation Bias
            last_sleep_report  TEXT DEFAULT '',       -- JSON of most recent consolidation report
            created_at  TEXT DEFAULT (datetime('now')),
            updated_at  TEXT DEFAULT (datetime('now'))
        );

        -- Cross-session memory: serialized working memory for each character
        CREATE TABLE IF NOT EXISTS session_state (
            character   TEXT PRIMARY KEY,
            turns       TEXT NOT NULL DEFAULT '[]',   -- JSON list of {role, content}
            last_question TEXT NOT NULL DEFAULT '',
            last_options TEXT,                         -- JSON list of Option dicts
            conversation_history TEXT DEFAULT '[]',    -- JSON list of {text, options, chosen}
            preferred_profile TEXT,                    -- JSON [T,B,D,C,P]
            created_at  TEXT DEFAULT (datetime('now')),
            updated_at  TEXT DEFAULT (datetime('now'))
        );

        -- Migration: add conversation_history column for existing DBs
        SELECT CASE
            WHEN COUNT(*) = 0 THEN 1
            ELSE 0
        END FROM pragma_table_info('session_state') WHERE name = 'conversation_history';
    """)
    conn.commit()

    # Migration: add conversation_history for existing production DBs
    try:
        conn.execute("ALTER TABLE session_state ADD COLUMN conversation_history TEXT DEFAULT '[]'")
        conn.commit()
    except Exception:
        pass

    # Migration: add last_sleep_report for DBs created before the column existed
    try:
        conn.execute("ALTER TABLE characters ADD COLUMN last_sleep_report TEXT DEFAULT ''")
        conn.commit()
    except Exception:
        pass


# ──────────────────────────────────────────────
#  Character CRUD
# ──────────────────────────────────────────────

def get_character(name: str) -> dict[str, Any] | None:
    conn = get_conn()
    row = conn.execute(
        "SELECT * FROM characters WHERE name = ?", (name,)
    ).fetchone()
    if row is None:
        return None
    return _deserialise(dict(row))


def upsert_character(data: dict[str, Any]) -> None:
    conn = get_conn()
    row = _serialise(data)
    conn.execute(
        """
        INSERT INTO characters
            (name, aliases, traits, relations, motivation, arc_stage,
             backstory, embedding_centroid, preferred_profile, last_sleep_report, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
        ON CONFLICT(name) DO UPDATE SET
            aliases           = excluded.aliases,
            traits            = excluded.traits,
            relations         = excluded.relations,
            motivation        = excluded.motivation,
            arc_stage         = excluded.arc_stage,
            backstory         = excluded.backstory,
            embedding_centroid = excluded.embedding_centroid,
            preferred_profile  = excluded.preferred_profile,
            last_sleep_report  = excluded.last_sleep_report,
            updated_at        = datetime('now')
        """,
        (
            row["name"],
            row["aliases"],
            row["traits"],
            row["relations"],
            row["motivation"],
            row["arc_stage"],
            row["backstory"],
            row["embedding_centroid"],
            row["preferred_profile"],
            row.get("last_sleep_report", ""),
        ),
    )
    conn.commit()


def list_characters() -> list[str]:
    conn = get_conn()
    rows = conn.execute("SELECT name FROM characters ORDER BY name").fetchall()
    return [r["name"] for r in rows]


# ──────────────────────────────────────────────
#  Session state CRUD (cross-session memory)
# ──────────────────────────────────────────────


def get_session_state(character: str) -> dict[str, Any] | None:
    """Load serialised working memory for a character, or None."""
    conn = get_conn()
    row = conn.execute(
        "SELECT * FROM session_state WHERE character = ?", (character,)
    ).fetchone()
    if row is None:
        return None
    return _deserialise(dict(row))


def upsert_session_state(data: dict[str, Any]) -> None:
    """Save or update serialised working memory for a character."""
    conn = get_conn()
    row = _serialise(data)
    conn.execute(
        """
        INSERT INTO session_state
            (character, turns, last_question, last_options, conversation_history, preferred_profile, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
        ON CONFLICT(character) DO UPDATE SET
            turns             = excluded.turns,
            last_question     = excluded.last_question,
            last_options      = excluded.last_options,
            conversation_history = COALESCE(excluded.conversation_history, session_state.conversation_history),
            preferred_profile = excluded.preferred_profile,
            updated_at        = datetime('now')
        """,
        (
            row["character"],
            row["turns"],
            row["last_question"],
            row.get("last_options"),
            row.get("conversation_history"),
            row.get("preferred_profile"),
        ),
    )
    conn.commit()


def delete_character(name: str) -> bool:
    """Delete a character and all associated data (events, session state)."""
    conn = get_conn()
    # Delete events & archives for this character
    conn.execute("DELETE FROM events WHERE protagonist = ?", (name,))
    conn.execute("DELETE FROM event_archive WHERE character = ?", (name,))
    # Delete session state
    conn.execute("DELETE FROM session_state WHERE character = ?", (name,))
    # Delete character entry
    cursor = conn.execute("DELETE FROM characters WHERE name = ?", (name,))
    conn.commit()
    # Also clean up ChromaDB events for this character
    try:
        from app.memory.vectors import VectorStore
        vs = VectorStore()
        events = vs.get_all_by_metadata("events", {"protagonist": name})
        if events and events.get("ids"):
            for event_id in events["ids"]:
                vs.delete("events", event_id)
    except Exception:
        pass  # best-effort cleanup
    return cursor.rowcount > 0


def delete_session_state(character: str) -> None:
    """Remove saved session state (e.g. after sleep consolidation)."""
    conn = get_conn()
    conn.execute("DELETE FROM session_state WHERE character = ?", (character,))
    conn.commit()


# ──────────────────────────────────────────────
#  Serialisation helpers
# ──────────────────────────────────────────────

def _serialise(data: dict[str, Any]) -> dict[str, Any]:
    """Convert Python objects to JSON strings for SQLite storage."""
    out = dict(data)
    for key in ("aliases", "traits", "relations", "embedding_centroid", "preferred_profile", "turns", "last_options", "conversation_history"):
        if key in out and not isinstance(out.get(key), str):
            out[key] = json.dumps(out[key], ensure_ascii=False)
    return out


def _deserialise(row: dict[str, Any]) -> dict[str, Any]:
    """Convert JSON strings back to Python objects."""
    out = dict(row)
    for key in ("aliases", "traits", "relations", "embedding_centroid", "preferred_profile", "turns", "last_options", "conversation_history"):
        val = out.get(key)
        if val and isinstance(val, str):
            try:
                out[key] = json.loads(val)
            except (json.JSONDecodeError, TypeError):
                pass
    return out

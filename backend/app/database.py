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
            created_at  TEXT DEFAULT (datetime('now')),
            updated_at  TEXT DEFAULT (datetime('now'))
        );
    """)
    conn.commit()


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
             backstory, embedding_centroid, preferred_profile, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
        ON CONFLICT(name) DO UPDATE SET
            aliases           = excluded.aliases,
            traits            = excluded.traits,
            relations         = excluded.relations,
            motivation        = excluded.motivation,
            arc_stage         = excluded.arc_stage,
            backstory         = excluded.backstory,
            embedding_centroid = excluded.embedding_centroid,
            preferred_profile  = excluded.preferred_profile,
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
        ),
    )
    conn.commit()


def list_characters() -> list[str]:
    conn = get_conn()
    rows = conn.execute("SELECT name FROM characters ORDER BY name").fetchall()
    return [r["name"] for r in rows]


# ──────────────────────────────────────────────
#  Serialisation helpers
# ──────────────────────────────────────────────

def _serialise(data: dict[str, Any]) -> dict[str, Any]:
    """Convert Python objects to JSON strings for SQLite storage."""
    out = dict(data)
    for key in ("aliases", "traits", "relations", "embedding_centroid", "preferred_profile"):
        if key in out and not isinstance(out.get(key), str):
            out[key] = json.dumps(out[key], ensure_ascii=False)
    return out


def _deserialise(row: dict[str, Any]) -> dict[str, Any]:
    """Convert JSON strings back to Python objects."""
    out = dict(row)
    for key in ("aliases", "traits", "relations", "embedding_centroid", "preferred_profile"):
        val = out.get(key)
        if val and isinstance(val, str):
            try:
                out[key] = json.loads(val)
            except (json.JSONDecodeError, TypeError):
                pass
    return out

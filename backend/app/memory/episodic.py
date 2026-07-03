"""Episodic memory — SQLite + vector retrieval (Zwaan-indexed events).

Includes time-based decay tracking (last_accessed_at, access_count) and
an event_archive table for consolidated memories below recall threshold.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from app.config import SQLITE_PATH
from app.models.event import NarrativeEvent


class EpisodicMemory:
    """Event-indexed episodic store backed by SQLite.

    Each event is indexed by (time, space, protagonist, causality, intent)
    — Zwaan's event-indexing model — plus a vector embedding for
    similarity search. Also tracks access frequency and time for decay.
    """

    def __init__(self, db_path: Path | str = SQLITE_PATH) -> None:
        self._path = Path(db_path)
        self._conn = sqlite3.connect(str(self._path), check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._init_db()

    def _init_db(self) -> None:
        self._conn.executescript("""
            CREATE TABLE IF NOT EXISTS events (
                id              TEXT PRIMARY KEY,
                chapter         INTEGER NOT NULL,
                position        TEXT NOT NULL DEFAULT '',
                protagonist     TEXT NOT NULL,
                summary         TEXT NOT NULL,
                importance      REAL NOT NULL DEFAULT 0.5,
                embedding       TEXT,          -- JSON float array
                related         TEXT,          -- JSON string array
                zwaan_dims      TEXT,          -- JSON dict
                emotion_tags    TEXT,          -- JSON string array (Plutchik emotions)
                last_accessed_at TEXT,         -- ISO timestamp of last /ask retrieval
                access_count    INTEGER DEFAULT 0,
                created_at      TEXT DEFAULT (datetime('now'))
            );
            CREATE INDEX IF NOT EXISTS idx_events_protag
                ON events(protagonist);
            CREATE INDEX IF NOT EXISTS idx_events_chapter
                ON events(chapter);
            -- Zwaan expression indexes: no schema change, just query-ready
            CREATE INDEX IF NOT EXISTS idx_events_zwaan_time
                ON events(json_extract(zwaan_dims, '$.time'));
            CREATE INDEX IF NOT EXISTS idx_events_zwaan_space
                ON events(json_extract(zwaan_dims, '$.space'));

            CREATE TABLE IF NOT EXISTS event_archive (
                id          TEXT PRIMARY KEY,
                original_id TEXT NOT NULL,
                character   TEXT NOT NULL,
                summary     TEXT NOT NULL,
                full_text   TEXT,            -- original full summary (for REM reference)
                importance  REAL NOT NULL,
                zwaan_dims  TEXT,            -- JSON dict
                archived_at TEXT DEFAULT (datetime('now'))
            );
            CREATE INDEX IF NOT EXISTS idx_archive_char
                ON event_archive(character);
        """)
        self._migrate_v2()
        self._migrate_v3()
        self._conn.commit()

    def _migrate_v2(self) -> None:
        """Add decay-tracking columns to existing databases."""
        for col in ("last_accessed_at", "access_count"):
            try:
                self._conn.execute(
                    f"ALTER TABLE events ADD COLUMN {col} TEXT"
                    if col == "last_accessed_at" else
                    f"ALTER TABLE events ADD COLUMN {col} INTEGER DEFAULT 0"
                )
            except sqlite3.OperationalError:
                pass  # column already exists

    def _migrate_v3(self) -> None:
        """Add Zwaan expression indexes for existing databases."""
        for idx_name, expr in (
            ("idx_events_zwaan_time", "json_extract(zwaan_dims, '$.time')"),
            ("idx_events_zwaan_space", "json_extract(zwaan_dims, '$.space')"),
        ):
            try:
                self._conn.execute(
                    f"CREATE INDEX IF NOT EXISTS {idx_name} ON events({expr})"
                )
            except sqlite3.OperationalError:
                pass

        # Set default last_accessed_at for existing rows
        try:
            self._conn.execute(
                "UPDATE events SET last_accessed_at = datetime('now') "
                "WHERE last_accessed_at IS NULL"
            )
        except sqlite3.OperationalError:
            pass

    # ── Event CRUD ──────────────────────────────────────

    def add_event(self, event: NarrativeEvent) -> None:
        self._conn.execute(
            """
            INSERT OR REPLACE INTO events
                (id, chapter, position, protagonist, summary,
                 importance, embedding, related, zwaan_dims,
                 last_accessed_at, access_count)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), 0)
            """,
            (
                event.id,
                event.chapter,
                event.position,
                event.protagonist,
                event.summary,
                event.importance,
                json.dumps(event.embedding) if event.embedding else None,
                json.dumps(event.related_entities),
                json.dumps(event.zwaan_dims),
            ),
        )
        self._conn.commit()

    def get_events(
        self,
        protagonist: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        """Get active (non-archived) events, optionally filtered by protagonist."""
        query = "SELECT * FROM events"
        params: list[Any] = []
        if protagonist:
            query += " WHERE protagonist = ?"
            params.append(protagonist)
        query += " ORDER BY chapter, position LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        rows = self._conn.execute(query, params).fetchall()
        return [dict(r) for r in rows]

    def get_event(self, event_id: str) -> dict[str, Any] | None:
        """Get a single event by ID."""
        row = self._conn.execute(
            "SELECT * FROM events WHERE id = ?", (event_id,)
        ).fetchone()
        return dict(row) if row else None

    def record_access(
        self, event_ids: list[str], boost: float = 0.01
    ) -> None:
        """Increment access_count and update last_accessed_at for given events.

        Also gives a small importance boost (capped at 1.0) to simulate
        the retrieval-practice effect — events that users keep asking about
        resist decay because they're clearly relevant.

        Called after a successful /ask generation. Non-blocking.
        """
        if not event_ids:
            return
        now_clause = "datetime('now')"
        ids_str = ",".join(f"'{eid}'" for eid in event_ids if eid)
        if not ids_str:
            return
        self._conn.execute(
            f"UPDATE events SET "
            f"  access_count = access_count + 1, "
            f"  last_accessed_at = {now_clause}, "
            f"  importance = MIN(1.0, importance + {boost}) "
            f"WHERE id IN ({ids_str})"
        )
        self._conn.commit()

    def update_importance(self, event_id: str, new_importance: float) -> None:
        """Update the importance score of an existing event."""
        self._conn.execute(
            "UPDATE events SET importance = ? WHERE id = ?",
            (new_importance, event_id),
        )
        self._conn.commit()

    def update_emotion_tags(
        self, event_id: str, tags: list[str]
    ) -> None:
        """Store Plutchik emotion tags for an event."""
        self._conn.execute(
            "UPDATE events SET emotion_tags = ? WHERE id = ?",
            (json.dumps(tags, ensure_ascii=False), event_id),
        )
        self._conn.commit()

    def delete_event(self, event_id: str) -> None:
        """Remove an event from the store."""
        self._conn.execute(
            "DELETE FROM events WHERE id = ?",
            (event_id,),
        )
        self._conn.commit()

    def get_max_chapter(self, protagonist: str | None = None) -> int:
        """Get the highest chapter number for a character (or overall)."""
        query = "SELECT COALESCE(MAX(chapter), 1) FROM events"
        params: list[Any] = []
        if protagonist:
            query += " WHERE protagonist = ?"
            params.append(protagonist)
        row = self._conn.execute(query, params).fetchone()
        return row[0] if row else 1

    def count_events(self, protagonist: str | None = None) -> int:
        query = "SELECT COUNT(*) FROM events"
        params: list[Any] = []
        if protagonist:
            query += " WHERE protagonist = ?"
            params.append(protagonist)
        return self._conn.execute(query, params).fetchone()[0]

    # ── Archive CRUD ────────────────────────────────────

    def archive_event(
        self, event_id: str, truncated_summary: str | None = None
    ) -> bool:
        """Move an event from active store to the archive.

        1. Reads the full event from events table.
        2. Inserts into event_archive.
        3. Deletes from events table.

        Returns True if successful, False if event wasn't found.
        """
        ev = self.get_event(event_id)
        if ev is None:
            return False

        full_summary = ev.get("summary", "")
        self._conn.execute(
            """
            INSERT OR REPLACE INTO event_archive
                (id, original_id, character, summary, full_text,
                 importance, zwaan_dims)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                f"archived_{event_id}",
                event_id,
                ev.get("protagonist", ""),
                truncated_summary or full_summary[:100],
                full_summary,
                ev.get("importance", 0.5),
                ev.get("zwaan_dims"),
            ),
        )
        self._conn.execute("DELETE FROM events WHERE id = ?", (event_id,))
        self._conn.commit()
        return True

    def get_archive(
        self,
        character: str | None = None,
        limit: int = 200,
    ) -> list[dict[str, Any]]:
        """Get archived events, optionally filtered by character."""
        query = "SELECT * FROM event_archive"
        params: list[Any] = []
        if character:
            query += " WHERE character = ?"
            params.append(character)
        query += " ORDER BY archived_at DESC LIMIT ? OFFSET 0"
        params.append(limit)

        rows = self._conn.execute(query, params).fetchall()
        return [dict(r) for r in rows]

    def count_archived(self, character: str | None = None) -> int:
        query = "SELECT COUNT(*) FROM event_archive"
        params: list[Any] = []
        if character:
            query += " WHERE character = ?"
            params.append(character)
        return self._conn.execute(query, params).fetchone()[0]

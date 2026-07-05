"""Sleep consolidation service — three-phase memory consolidation cycle.

Analogous to the human sleep cycle:
  Phase 1 (NREM/SWS) — Conflict detection, importance adjustment
  Phase 2 (REM)      — LLM pattern extraction + vector redundancy pruning
                       + emotion tagging + arc progression + confidence adjustment
  Phase 3            — Consolidation report

Hybrid approach (per internal/SleepCycle-实现方案对比.md):
  - Pattern extraction: LLM prompt-based (top-20 events)
  - Redundancy pruning: ChromaDB pairwise L2 distance
  - Emotion decoupling: LLM Plutchik tagging
  - Arc / confidence: rule-based (unchanged)
"""

from __future__ import annotations

import json
import logging
from typing import Any

from openai import AsyncOpenAI

from app.config import (
    QWEN_API_KEY,
    QWEN_BASE_URL,
    QWEN_MODEL,
    QWEN_EMBEDDING_MODEL,
)
from app.database import get_character, upsert_character
from app.memory.episodic import EpisodicMemory
from app.memory.vectors import VectorStore
from app.services.decay import recall_score, classify

logger = logging.getLogger(__name__)

# ── Config ──────────────────────────────────────────────

_CONFLICT_MAP: dict[str, set[str]] = {
    "avoid": {"brave", "courageous", "bold", "fearless", "reckless",
              "confrontational", "charge", "head-on"},
    "submit": {"dominant", "proud", "defiant", "rebellious",
               "defy", "unbowed", "unyielding"},
    "retreat": {"persistent", "stubborn", "determined", "resolute",
                "unrelenting", "tenacious", "steadfast"},
    "betray": {"loyal", "faithful", "devoted", "true",
               "system", "order", "rule-bound", "rule-driven",
               "unquestioning", "pack", "hierarchy"},
    "deceive": {"honest", "honorable", "forthright", "direct", "truthful",
                "upright", "aboveboard"},
    "hesitate": {"decisive", "resolute", "unwavering", "confident",
                 "unhesitating", "certain"},
    "flee": {"protective", "guardian", "defender", "fearless",
             "steadfast", "unyielding", "face danger"},
}

_PIVOTAL_KEYWORDS = [
    "betray", "death", "discover", "revelation", "confrontation",
    "sacrifice", "bond", "sever", "choose", "cross",
]

_ARC_TRANSITION_THRESHOLD = 3

# REM — hybrid config
_PATTERN_SAMPLE_SIZE = 20       # top-N events for LLM pattern extraction
_EMOTION_SAMPLE_SIZE = 10       # top-N events for LLM emotion tagging
_PRUNE_DISTANCE_THRESHOLD = 0.05  # L2 distance below this → redundant
_PRUNE_MIN_IMPORTANCE = 0.3     # only prune events at or below this weight


# ── Clients (lazy init) ─────────────────────────────────

_openai_client: AsyncOpenAI | None = None


def _get_llm() -> AsyncOpenAI:
    global _openai_client
    if _openai_client is None:
        _openai_client = AsyncOpenAI(
            api_key=QWEN_API_KEY, base_url=QWEN_BASE_URL
        )
    return _openai_client


# ── Report data class ───────────────────────────────────


class ConsolidationReport:
    """Structured output of a sleep cycle."""

    def __init__(self, character: str) -> None:
        self.character = character
        self.phase1: dict[str, Any] = {
            "events_analyzed": 0,
            "conflicts_detected": [],
            "importance_adjustments": [],
            "events_archived": 0,
        }
        self.phase2: dict[str, Any] = {
            "patterns_extracted": [],
            "events_pruned": 0,
            "events_tagged": 0,
            "trait_updates": [],
            "arc_stage_change": None,
        }
        self.phase3: dict[str, Any] = {
            "summary": "",
            "confidence_delta": 0.0,
        }


# ── Service ─────────────────────────────────────────────


class SleepService:
    """Three-phase memory consolidation for a character."""

    def __init__(self, episodic: EpisodicMemory) -> None:
        self._episodic = episodic
        self._vectors = VectorStore()

    # ══════════════════════════════════════════════════════
    #  Public API
    # ══════════════════════════════════════════════════════

    async def consolidate(self, character_name: str) -> dict[str, Any]:
        """Run the full sleep cycle for a character.

        Returns the consolidation report as a JSON-serialisable dict.
        """
        report = ConsolidationReport(character_name)

        char_data = get_character(character_name)
        if char_data is None:
            return {"status": "error",
                    "message": f"Character '{character_name}' not found"}

        events = self._episodic.get_events(
            protagonist=character_name, limit=500
        )
        if not events:
            return {
                "status": "ok",
                "character": character_name,
                "message": "No events to consolidate",
                "report": {},
            }

        # ── Phase 1 — fact consolidation ──
        event_impacts = self._phase1_fact_consolidation(events, char_data, report)
        for event_id, new_imp in event_impacts:
            self._episodic.update_importance(event_id, new_imp)

        # ── Phase 1.5 — decay archive ──
        archived = self._phase1_decay_archive(events, char_data, report)

        # ── Phase 2 — REM (hybrid) ──
        await self._phase2_rem(events, char_data, report)

        # ── Phase 3 — summary ──
        self._phase3_generate_report(report)

        # Persist character updates
        upsert_character(char_data)

        return {
            "status": "ok",
            "character": character_name,
            "message": "Sleep cycle complete",
            "report": {
                "phase1": report.phase1,
                "phase2": report.phase2,
                "phase3": report.phase3,
            },
        }

    # ══════════════════════════════════════════════════════
    #  Phase 1 — 事实巩固  (NREM/SWS)
    # ══════════════════════════════════════════════════════

    def _phase1_fact_consolidation(
        self,
        events: list[dict[str, Any]],
        char_data: dict[str, Any],
        report: ConsolidationReport,
    ) -> list[tuple[str, float]]:
        """Analyze events for conflicts and importance adjustments.

        Returns a list of (event_id, new_importance) tuples to persist.
        """
        report.phase1["events_analyzed"] = len(events)
        traits = char_data.get("traits", [])
        trait_descriptors: list[str] = []
        for t in traits:
            trait_descriptors.append(t.get("name", ""))
            desc = t.get("description", "")
            if desc:
                trait_descriptors.append(desc)
        descriptor_text = " ".join(trait_descriptors).lower()

        importance_updates: list[tuple[str, float]] = []

        for ev in events:
            raw_imp = ev.get("importance", 0.5)
            zwaan = self._parse_zwaan(ev)
            intent = (zwaan.get("intent", "") or "").lower()
            cause = (zwaan.get("causality", "") or "").lower()
            summary = ev.get("summary", "") or ""

            self._detect_conflicts(intent, descriptor_text, summary, raw_imp, report)
            new_imp = self._adjust_importance(raw_imp, cause, summary, report)

            if abs(new_imp - raw_imp) > 0.01:
                importance_updates.append((ev["id"], new_imp))

        return importance_updates

    def _detect_conflicts(
        self,
        intent: str,
        descriptor_text: str,
        summary: str,
        importance: float,
        report: ConsolidationReport,
    ) -> None:
        """Check if an event's intent contradicts known character traits."""
        for conflict_intent, conflicting_keywords in _CONFLICT_MAP.items():
            if conflict_intent not in intent:
                continue
            matched = {kw for kw in conflicting_keywords if kw in descriptor_text}
            if not matched:
                continue
            report.phase1["conflicts_detected"].append({
                "intent": intent,
                "conflicting_keywords": sorted(matched),
                "event": summary[:80],
                "severity": "high" if importance > 0.7
                           else "medium" if importance > 0.4
                           else "low",
            })

    def _adjust_importance(
        self,
        current: float,
        cause: str,
        summary: str,
        report: ConsolidationReport,
    ) -> float:
        """Boost importance for emotionally or narratively pivotal events."""
        for kw in _PIVOTAL_KEYWORDS:
            if kw in cause or kw in summary.lower():
                new_imp = min(1.0, current + 0.15)
                report.phase1["importance_adjustments"].append({
                    "event": summary[:60],
                    "from": current,
                    "to": new_imp,
                    "reason": f"pivotal keyword: '{kw}'",
                })
                return new_imp
        return current

    # ══════════════════════════════════════════════════════
    #  Phase 1.5 — 衰减归档 (Decay Archive)
    # ══════════════════════════════════════════════════════

    def _phase1_decay_archive(
        self,
        events: list[dict[str, Any]],
        char_data: dict[str, Any],
        report: ConsolidationReport,
    ) -> int:
        """Archive events whose recall_score has fallen below the archive threshold.

        Events are moved from the active events table to the event_archive table,
        and their vector embeddings are removed from ChromaDB.
        """
        char_name = char_data.get("name", "")
        current_chapter = self._episodic.get_max_chapter(char_name)
        archived_count = 0

        for ev in events:
            chapter = ev.get("chapter", 1) or 1
            imp = ev.get("importance", 0.5) or 0.5
            score = recall_score(imp, current_chapter - chapter)
            if classify(score) != "archived":
                continue

            ev_id = ev.get("id", "")
            if not ev_id:
                continue

            # Move to archive
            summary = ev.get("summary", "")
            truncated = summary[:100] if len(summary) > 100 else summary
            success = self._episodic.archive_event(ev_id, truncated)
            if not success:
                continue

            # Also remove from ChromaDB
            try:
                self._vectors.delete("events", ev_id)
            except Exception:
                pass  # Vector may not exist — not an error

            archived_count += 1

        report.phase1["events_archived"] = archived_count
        return archived_count

    # ══════════════════════════════════════════════════════
    #  Phase 2 — 抽象整合  (REM)  —  Hybrid
    # ══════════════════════════════════════════════════════

    async def _phase2_rem(
        self,
        events: list[dict[str, Any]],
        char_data: dict[str, Any],
        report: ConsolidationReport,
    ) -> None:
        """REM stage: ① LLM pattern extraction → ② vector pruning → ③ emotion tagging → ④ arc/trait adjustment."""
        # Sort by importance descending
        sorted_events = sorted(events, key=lambda e: e.get("importance", 0), reverse=True)

        # ── ① LLM pattern extraction ──
        sample = sorted_events[:_PATTERN_SAMPLE_SIZE]

        # Also include archived events for long-term pattern context
        archived_events = self._episodic.get_archive(
            character=char_data["name"], limit=15
        )
        if archived_events:
            # Mark archived events so the LLM knows they're historical
            for ae in archived_events:
                ae["summary"] = "[Archived] " + ae.get("summary", "")
            sample = sample + archived_events

        patterns = await self._extract_patterns_llm(char_data, sample)
        if patterns:
            char_data["behavior_patterns"] = patterns
            report.phase2["patterns_extracted"] = patterns

        # ── ② Vector redundancy pruning ──
        pruned = await self._prune_redundant_events(char_data["name"])
        report.phase2["events_pruned"] = pruned

        # ── ③ LLM emotion tagging ──
        emotion_sample = sorted_events[:_EMOTION_SAMPLE_SIZE]
        tagged = await self._tag_emotions_llm(char_data["name"], emotion_sample)
        report.phase2["events_tagged"] = tagged

        # ── ④ Arc stage + trait confidence (keep existing logic) ──
        self._update_arc_and_traits(char_data, report)

    # ── ① Pattern extraction (LLM) ──────────────────────

    async def _extract_patterns_llm(
        self,
        char_data: dict[str, Any],
        events: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Send top events to LLM and extract structured behavior patterns."""
        if not events:
            return []

        events_text = "\n\n".join(
            f"Event {i+1} (importance={e.get('importance', 0):.2f}): {e.get('summary', '')}"
            for i, e in enumerate(events)
        )

        prompt = (
            f"You are a literary behaviour analyst. Analyze character "
            f"'{char_data['name']}' based on their recent narrative events.\n\n"
            f"Backstory: {char_data.get('backstory', '')}\n"
            f"Known traits: {self._trait_summary(char_data)}\n\n"
            f"Events (sorted by narrative importance):\n{events_text}\n\n"
            f"Extract 1-3 behavioural patterns that describe how this character "
            f"repeatedly acts. Each pattern must be:\n"
            f"- A specific if-then rule (when X happens, the character does Y)\n"
            f"- Grounded in the event evidence above\n"
            f"- Different: each pattern should capture a distinct behavioural facet\n\n"
            f"Return ONLY valid JSON, no other text:\n"
            f'{{"patterns": [\n'
            f'  {{"condition": "when…", "behavior": "the character…", '
            f'"evidence_count": 2, "confidence": 0.75}},\n'
            f"  ...\n"
            f"]}}\n"
        )

        client = _get_llm()
        try:
            resp = await client.chat.completions.create(
                model=QWEN_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=1024,
            )
            content = resp.choices[0].message.content or "{}"
            return self._parse_patterns(content)
        except Exception as exc:
            logger.warning("Pattern extraction LLM call failed: %s", exc)
            return []

    # ── ② Redundancy pruning (vector) ───────────────────

    async def _prune_redundant_events(self, character_name: str) -> int:
        """Find near-duplicate events via ChromaDB and remove the less important one.

        Uses L2 distance between embeddings. Pairs below threshold with
        one event at or below PRUNE_MIN_IMPORTANCE → delete the low-importance one.
        """
        try:
            raw = self._vectors.get_all_by_metadata(
                collection="events",
                where={"protagonist": character_name},
            )
        except Exception:
            return 0

        ids = raw.get("ids", [])
        embeddings = raw.get("embeddings") or []
        metadatas = raw.get("metadatas", [])
        if not ids or len(ids) < 2:
            return 0

        # Map id → importance from metadata
        id_to_meta = {ids[i]: metadatas[i] for i in range(len(ids))}
        # Also get importance from SQLite
        id_to_imp: dict[str, float] = {}
        for evt in self._episodic.get_events(protagonist=character_name, limit=500):
            id_to_imp[evt["id"]] = evt.get("importance", 0.5)

        pruned = 0
        checked = set()

        for i in range(len(ids)):
            if ids[i] in checked:
                continue
            for j in range(i + 1, len(ids)):
                if ids[j] in checked:
                    continue
                # L2 distance between embeddings
                emb_i = embeddings[i]
                emb_j = embeddings[j]
                if not emb_i or not emb_j:
                    continue
                dist = sum((a - b) ** 2 for a, b in zip(emb_i, emb_j)) ** 0.5
                if dist >= _PRUNE_DISTANCE_THRESHOLD:
                    continue

                # Close pair — decide which to delete
                imp_i = id_to_imp.get(ids[i], 0.5)
                imp_j = id_to_imp.get(ids[j], 0.5)
                if imp_i <= _PRUNE_MIN_IMPORTANCE and imp_j > imp_i:
                    victim = ids[i]
                elif imp_j <= _PRUNE_MIN_IMPORTANCE and imp_i > imp_j:
                    victim = ids[j]
                else:
                    # Both above threshold or equal — skip
                    continue

                # Delete from both stores
                self._vectors.delete("events", victim)
                self._episodic.delete_event(victim)
                checked.add(victim)
                pruned += 1

        return pruned

    # ── ③ Emotion tagging (LLM) ─────────────────────────

    async def _tag_emotions_llm(
        self,
        character_name: str,
        events: list[dict[str, Any]],
    ) -> int:
        """Tag top events with Plutchik basic emotions via LLM."""
        if not events:
            return 0

        events_text = "\n\n".join(
            f"Event {i+1} (id={e['id']}): {e.get('summary', '')}"
            for i, e in enumerate(events)
        )

        prompt = (
            f"For character '{character_name}', tag each event below with "
            f"emotions from Plutchik's wheel of emotions:\n"
            f"joy, trust, fear, surprise, sadness, disgust, anger, anticipation\n\n"
            f"Choose 1-3 emotions per event. Return ONLY valid JSON:\n"
            f'{{"tags": [\n'
            f'  {{"id": "evt_xxx", "emotions": ["fear", "anticipation"]}},\n'
            f"  ...\n"
            f"]}}\n\n"
            f"Events:\n{events_text}\n"
        )

        client = _get_llm()
        try:
            resp = await client.chat.completions.create(
                model=QWEN_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=1024,
            )
            content = resp.choices[0].message.content or "{}"
            tags_list = self._parse_emotion_tags(content)
        except Exception as exc:
            logger.warning("Emotion tagging LLM call failed: %s", exc)
            return 0

        # Write tags back to events table
        for item in tags_list:
            eid = item.get("id", "")
            emotions = item.get("emotions", [])
            if eid and emotions:
                self._episodic.update_emotion_tags(eid, emotions)

        return len(tags_list)

    # ── ④ Arc stage + trait confidence ──────────────────

    def _update_arc_and_traits(
        self,
        char_data: dict[str, Any],
        report: ConsolidationReport,
    ) -> None:
        """Arc stage progression + trait confidence (unchanged from original)."""
        conflicts = report.phase1.get("conflicts_detected", [])
        traits: list[dict[str, Any]] = char_data.get("traits", [])

        # Arc stage progression
        if len(conflicts) >= _ARC_TRANSITION_THRESHOLD:
            old_stage = char_data.get("arc_stage", "unknown")
            new_stage = self._infer_arc_stage(old_stage, conflicts)
            if new_stage != old_stage:
                report.phase2["arc_stage_change"] = {
                    "from": old_stage,
                    "to": new_stage,
                    "reason": (
                        f"{len(conflicts)} behavioral conflicts detected — "
                        f"character behavior is deviating from established patterns"
                    ),
                }
                char_data["arc_stage"] = new_stage

        # Trait confidence adjustment
        for trait in traits:
            if trait.get("category") != "core":
                continue
            trait_name = trait.get("name", "").lower()
            trait_was_conflicted = any(
                trait_name in str(c.get("conflicting_keywords", [])).lower()
                for c in conflicts
            )
            if not trait_was_conflicted:
                old_conf = trait.get("confidence", 0.5)
                new_conf = min(1.0, old_conf + 0.02)
                trait["confidence"] = round(new_conf, 3)
            else:
                old_conf = trait.get("confidence", 0.5)
                new_conf = max(0.1, old_conf - 0.03)
                trait["confidence"] = round(new_conf, 3)
                report.phase2["trait_updates"].append({
                    "trait": trait.get("name", ""),
                    "action": "confidence_decreased",
                    "from": round(old_conf, 3),
                    "to": new_conf,
                })

    def _infer_arc_stage(
        self,
        current: str,
        conflicts: list[dict[str, Any]],
    ) -> str:
        """Simple arc stage progression based on conflict patterns."""
        stages = [
            "stable",
            "initial",
            "denial",
            "turmoil",
            "questioning",
            "transformation",
            "resolution",
            "new_normal",
        ]
        try:
            idx = stages.index(current.split(" —")[0].strip())
        except ValueError:
            idx = stages.index("stable") if "stable" in current else -1

        if idx < 0:
            return "turmoil"
        return stages[min(idx + 1, len(stages) - 1)]

    # ══════════════════════════════════════════════════════
    #  Phase 3 — 报告生成
    # ══════════════════════════════════════════════════════

    def _phase3_generate_report(self, report: ConsolidationReport) -> None:
        """Compile human-readable summary."""
        parts: list[str] = []
        p1 = report.phase1
        p2 = report.phase2

        parts.append(f"📊 Analyzed {p1['events_analyzed']} events")
        if p1["conflicts_detected"]:
            parts.append(f"⚡ Found {len(p1['conflicts_detected'])} behavioral conflict(s)")
        else:
            parts.append("✅ No behavioral conflicts detected")
        if p1["importance_adjustments"]:
            parts.append(f"🔺 Adjusted importance for {len(p1['importance_adjustments'])} key event(s)")
        if p1.get("events_archived", 0):
            parts.append(f"📦 Archived {p1['events_archived']} outdated memory event(s)")
        if p2["patterns_extracted"]:
            parts.append(f"🧩 Extracted {len(p2['patterns_extracted'])} behavioral pattern(s)")
        if p2["events_pruned"]:
            parts.append(f"✂️ Pruned {p2['events_pruned']} redundant event(s)")
        if p2["events_tagged"]:
            parts.append(f"🏷️ Tagged {p2['events_tagged']} event(s) with emotional labels")
        if p2["arc_stage_change"]:
            parts.append(f"🔄 Arc evolution: {p2['arc_stage_change']['from']} → {p2['arc_stage_change']['to']}")
        if p2["trait_updates"]:
            parts.append(f"📉 {len(p2['trait_updates'])} trait confidence downgraded")
        report.phase3["summary"] = " | ".join(parts)

        delta = len(p2.get("trait_updates", [])) * -0.03
        report.phase3["confidence_delta"] = round(delta, 3)

    # ══════════════════════════════════════════════════════
    #  Helpers
    # ══════════════════════════════════════════════════════

    @staticmethod
    def _parse_zwaan(event: dict[str, Any]) -> dict[str, str]:
        """Safely parse the zwaan_dims field (may be JSON string or dict)."""
        raw = event.get("zwaan_dims")
        if raw is None:
            return {}
        if isinstance(raw, dict):
            return raw
        try:
            return json.loads(raw) if isinstance(raw, str) else {}
        except (json.JSONDecodeError, TypeError):
            return {}

    @staticmethod
    def _trait_summary(char_data: dict[str, Any]) -> str:
        """Compact trait description for LLM prompts."""
        traits = char_data.get("traits", [])
        return "; ".join(
            f"{t.get('name', '?')} ({t.get('category', '?')}): {t.get('description', '')}"
            for t in traits
        )

    @staticmethod
    def _parse_patterns(raw: str) -> list[dict[str, Any]]:
        """Parse the JSON response from pattern extraction LLM call."""
        import re
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if not match:
            return []
        try:
            data = json.loads(match.group())
            return data.get("patterns", [])
        except (json.JSONDecodeError, TypeError):
            return []

    @staticmethod
    def _parse_emotion_tags(raw: str) -> list[dict[str, Any]]:
        """Parse the JSON response from emotion tagging LLM call."""
        import re
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if not match:
            return []
        try:
            data = json.loads(match.group())
            return data.get("tags", [])
        except (json.JSONDecodeError, TypeError):
            return []

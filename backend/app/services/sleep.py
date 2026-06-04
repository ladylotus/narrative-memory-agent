"""Sleep consolidation service — three-phase memory consolidation cycle.

Analogous to the human sleep cycle:
  Phase 1 (NREM/SWS) — Episodic → semantic migration, conflict detection
  Phase 2 (REM)      — Pattern extraction, redundancy pruning
  Phase 3            — Consolidation report
"""

from __future__ import annotations

import json
import logging
from typing import Any

from app.database import get_character, upsert_character
from app.memory.episodic import EpisodicMemory

logger = logging.getLogger(__name__)

# ── Config ──────────────────────────────────────────────
_CONFLICT_MAP: dict[str, set[str]] = {
    "avoid": {"brave", "courageous", "bold", "fearless", "reckless",
              "勇敢", "无畏", "果断", "冲", "直面", "迎战", "confrontational"},
    "submit": {"dominant", "proud", "defiant", "rebellious",
               "主导", "骄傲", "不驯", "反抗", "反叛", "不屈", "defy"},
    "retreat": {"persistent", "stubborn", "determined", "resolute",
                "坚持", "固执", "坚定", "不退", "守", "绝不"},
    "betray": {"loyal", "faithful", "devoted", "true",
               "忠诚", "忠贞", "信赖", "信任", "忠心",
               "框架", "规则", "秩序", "体系", "system", "order",
               "规则驱动", "框架内", "从未质疑", "pack", "守序"},
    "deceive": {"honest", "honorable", "forthright", "direct", "truthful",
                "诚实", "正直", "直接", "光明", "坦荡"},
    "hesitate": {"decisive", "resolute", "unwavering", "confident",
                 "果断", "坚定", "自信", "从不犹豫", "确信"},
    "flee": {"protective", "guardian", "defender", "fearless",
             "保护", "守护", "无畏", "担当", "承担", "不退让", "直面"},
}

_PIVOTAL_KEYWORDS = [
    "betray", "death", "discover", "revelation", "confrontation",
    "sacrifice", "bond", "sever", "choose", "cross",
]

_ARC_TRANSITION_THRESHOLD = 3  # conflicts needed to trigger arc detection


# ── Service ─────────────────────────────────────────────


class ConsolidationReport:
    """Structured output of a sleep cycle."""

    def __init__(self, character: str) -> None:
        self.character = character
        self.phase1: dict[str, Any] = {
            "events_analyzed": 0,
            "conflicts_detected": [],
            "importance_adjustments": [],
        }
        self.phase2: dict[str, Any] = {
            "patterns_extracted": [],
            "events_pruned": 0,
            "trait_updates": [],
            "arc_stage_change": None,
        }
        self.phase3: dict[str, Any] = {
            "summary": "",
            "confidence_delta": 0.0,
        }


class SleepService:
    """Three-phase memory consolidation for a character."""

    def __init__(self, episodic: EpisodicMemory) -> None:
        self._episodic = episodic

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
            return {"status": "error", "message": f"Character '{character_name}' not found"}

        events = self._episodic.get_events(protagonist=character_name, limit=500)
        if not events:
            return {
                "status": "ok",
                "character": character_name,
                "message": "No events to consolidate",
                "report": {},
            }

        # ── Phase 1 ──
        event_impacts = self._phase1_fact_consolidation(events, char_data, report)

        # Apply importance updates to events in DB
        for event_id, new_imp in event_impacts:
            self._episodic.update_importance(event_id, new_imp)

        # ── Phase 2 ──
        self._phase2_abstract_integration(char_data, report)

        # ── Phase 3 ──
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
        # Build keyword-rich trait descriptors: names + description tokens
        trait_descriptors: list[str] = []
        for t in traits:
            trait_descriptors.append(t.get("name", ""))
            desc = t.get("description", "")
            if desc:
                # Extract meaningful Chinese fragments
                trait_descriptors.append(desc)
        descriptor_text = " ".join(trait_descriptors).lower()

        importance_updates: list[tuple[str, float]] = []

        for ev in events:
            raw_imp = ev.get("importance", 0.5)
            zwaan = self._parse_zwaan(ev)
            intent = (zwaan.get("intent", "") or "").lower()
            cause = (zwaan.get("cause", "") or "").lower()
            summary = ev.get("summary", "") or ""

            # ── Conflict detection ──
            self._detect_conflicts(intent, descriptor_text, summary, raw_imp, report)

            # ── Pivotal event boost ──
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
        """Check if an event's intent contradicts known character traits.

        Matches against trait names AND descriptions, enabling detection
        even for Chinese-named traits.
        """
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
    #  Phase 2 — 抽象整合  (REM)
    # ══════════════════════════════════════════════════════

    def _phase2_abstract_integration(
        self,
        char_data: dict[str, Any],
        report: ConsolidationReport,
    ) -> None:
        """Extract behavioral patterns and update semantic memory."""
        conflicts = report.phase1.get("conflicts_detected", [])
        traits: list[dict[str, Any]] = char_data.get("traits", [])

        # ── Arc stage progression ──
        if len(conflicts) >= _ARC_TRANSITION_THRESHOLD:
            old_stage = char_data.get("arc_stage", "unknown")
            # Determine the new stage based on current stage
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

        # ── Trait confidence adjustment ──
        for trait in traits:
            if trait.get("category") != "core":
                continue
            trait_name = trait.get("name", "").lower()
            # If core trait is never conflicted, confidence increases slightly
            trait_was_conflicted = any(
                trait_name in str(c.get("conflicting_keywords", [])).lower()
                for c in conflicts
            )
            if not trait_was_conflicted:
                old_conf = trait.get("confidence", 0.5)
                new_conf = min(1.0, old_conf + 0.02)
                trait["confidence"] = round(new_conf, 3)
            else:
                # Trait was challenged — slight confidence decrease
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
        # The stages represent a character's narrative arc progression
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
        # Find current stage index
        try:
            idx = stages.index(current.split(" —")[0].strip())
        except ValueError:
            idx = stages.index("stable") if "stable" in current else -1

        if idx < 0:
            return "turmoil"  # Unknown stage → turmoil

        # Advance one stage if there are significant conflicts
        return stages[min(idx + 1, len(stages) - 1)]

    # ══════════════════════════════════════════════════════
    #  Phase 3 — 报告生成
    # ══════════════════════════════════════════════════════

    def _phase3_generate_report(self, report: ConsolidationReport) -> None:
        """Compile human-readable summary."""
        parts: list[str] = []
        p1 = report.phase1
        p2 = report.phase2

        parts.append(f"📊 分析了 {p1['events_analyzed']} 个事件")
        if p1["conflicts_detected"]:
            parts.append(f"⚡ 发现 {len(p1['conflicts_detected'])} 处行为冲突")
        else:
            parts.append("✅ 未发现行为冲突")
        if p1["importance_adjustments"]:
            parts.append(f"🔺 调整了 {len(p1['importance_adjustments'])} 个关键事件的权重")
        if p2["arc_stage_change"]:
            parts.append(f"🔄 角色弧光: {p2['arc_stage_change']['from']} → {p2['arc_stage_change']['to']}")
        if p2["trait_updates"]:
            parts.append(f"📉 {len(p2['trait_updates'])} 个特质置信度下调")
        report.phase3["summary"] = " | ".join(parts)

        # Confidence delta (net change)
        delta = len(p2.get("trait_updates", [])) * -0.03
        report.phase3["confidence_delta"] = round(delta, 3)

    # ── Helpers ────────────────────────────────────────

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

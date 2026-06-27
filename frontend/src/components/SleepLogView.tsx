"use client";

import type { Character } from "@/lib/types";
import type { SleepReport } from "@/lib/sleep-types";

export default function SleepLogView({
  char,
  report,
  onRunSleep,
}: {
  char: Character;
  report: SleepReport | null;
  onRunSleep: () => void;
}) {
  const shortName = char.name.split(" ")[0];

  if (!report) {
    return (
      <div className="scroll">
        <div className="page">
          <div className="page-head">
            <div className="page-title">💤 Sleep Consolidation Log</div>
            <div className="page-desc">
              During downtime, the agent replays recent events and reorganizes its memory of {shortName} —
              consolidating facts, abstracting patterns, and self-auditing.
            </div>
          </div>
          <div className="empty" style={{ marginTop: 40 }}>
            <div className="e-mark">💤</div>
            <div className="e-title">No consolidation records yet</div>
            <div className="e-desc">
              Run a sleep cycle and the agent will analyze all of {shortName}'s events,
              detect behavioral conflicts, and update the cognitive profile.
            </div>
            <div className="row-actions" style={{ marginTop: 20, justifyContent: "center" }}>
              <button className="btn primary" onClick={onRunSleep}>
                🌙 Run Sleep Consolidation
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  const p1 = report.phase1;
  const p2 = report.phase2;
  const p3 = report.phase3;
  const conflictCount = p1.conflicts_detected.length;

  const severityColor = (s: string) => {
    switch (s) {
      case "high": return "var(--risk-high)";
      case "medium": return "var(--risk-med)";
      default: return "var(--risk-low)";
    }
  };

  return (
    <div className="scroll">
      <div className="page">
        {/* Header */}
        <div className="page-head">
          <div className="page-title">💤 Sleep Consolidation Log</div>
          <div className="page-desc">
            Latest memory consolidation analysis for {shortName}
          </div>
        </div>

        {/* Summary card */}
        <div className="log-summary">
          <div className="ls-item">
            <span className="ls-k">📊 Events</span>
            <span className="ls-v">{p1.events_analyzed}</span>
          </div>
          <div className="ls-sep" />
          <div className="ls-item">
            <span className="ls-k">⚡ Conflicts</span>
            <span className="ls-v" style={{ color: conflictCount > 0 ? "var(--risk-med)" : "var(--risk-low)" }}>
              {conflictCount}
            </span>
          </div>
          <div className="ls-sep" />
          <div className="ls-item">
            <span className="ls-k">🔺 Adjustments</span>
            <span className="ls-v">{p1.importance_adjustments.length}</span>
          </div>
          <div className="ls-sep" />
          <div className="ls-item">
            <span className="ls-k">📉 Confidence</span>
            <span className="ls-v" style={{ color: p3.confidence_delta < 0 ? "var(--risk-med)" : "var(--risk-low)" }}>
              {p3.confidence_delta > 0 ? "+" : ""}{p3.confidence_delta}
            </span>
          </div>
        </div>

        {/* Phase 1: Fact Consolidation */}
        <div className="phase">
          <div className="phase-head">
            <span className="phase-num">1</span>
            <span className="phase-title">💤 Fact Consolidation</span>
          </div>
          <div className="phase-sub">Extract facts from events, detect contradictions with known traits</div>

          {conflictCount > 0 && (
            <div style={{ marginTop: 12, fontSize: 12, fontWeight: 600, color: "var(--risk-med)" }}>
              Detected {conflictCount} behavioral conflict(s):
            </div>
          )}
          {p1.conflicts_detected.map((c, i) => (
            <div className="log-entry" key={i} style={{ borderLeft: `3px solid ${severityColor(c.severity)}` }}>
              <div style={{ fontSize: 13 }}>{c.event}</div>
              <div style={{ fontSize: 11, color: "var(--ink-3)", marginTop: 4 }}>
                <span style={{ color: severityColor(c.severity) }}>
                  {c.severity === "high" ? "🔴" : c.severity === "medium" ? "🟡" : "🟢"}
                </span>
                {" "}Intent "{c.intent}" conflicts with trait "{c.conflicting_keywords.join(", ")}"
              </div>
            </div>
          ))}

          {p1.importance_adjustments.length > 0 && (
            <div style={{ marginTop: 12, fontSize: 12, fontWeight: 600, color: "var(--accent)" }}>
              Key event importance adjustments:
            </div>
          )}
          {p1.importance_adjustments.map((a, i) => (
            <div className="log-entry" key={`imp_${i}`}>
              <div style={{ fontSize: 12 }}>{a.event.slice(0, 60)}…</div>
              <div style={{ fontSize: 11, color: "var(--ink-3)" }}>
                🔺 {a.from} → {Math.round(a.to * 100) / 100}（{a.reason}）
              </div>
            </div>
          ))}
        </div>

        {/* Phase 2: Abstraction & Integration */}
        <div className="phase">
          <div className="phase-head">
            <span className="phase-num">2</span>
            <span className="phase-title">🧩 Abstraction & Integration</span>
          </div>
          <div className="phase-sub">Extract behavior patterns, update character understanding</div>

          {p2.arc_stage_change && (
            <div className="log-entry" style={{ borderLeft: "3px solid var(--accent)" }}>
              <div style={{ fontSize: 13, fontWeight: 600 }}>🔄 Arc Evolution</div>
              <div style={{ fontSize: 12, color: "var(--ink-3)", marginTop: 4 }}>
                {p2.arc_stage_change.from} → {p2.arc_stage_change.to}
              </div>
              <div style={{ fontSize: 11, color: "var(--ink-4)", marginTop: 4 }}>
                {p2.arc_stage_change.reason}
              </div>
            </div>
          )}

          {p2.trait_updates.length > 0 && (
            <div style={{ marginTop: 12, fontSize: 12, fontWeight: 600, color: "var(--risk-med)" }}>
              Trait confidence adjustments:
            </div>
          )}
          {p2.trait_updates.map((t, i) => (
            <div className="log-entry" key={`trait_${i}`}>
              <span style={{ fontSize: 12 }}>
                📉 {t.trait}：{t.from} → {t.to}
              </span>
            </div>
          ))}

          {p2.events_pruned > 0 && (
            <div className="log-entry">
              <span style={{ fontSize: 12 }}>✂️ Pruned {p2.events_pruned} low-weight events</span>
            </div>
          )}
        </div>

        {/* Phase 3: Self-Audit Report */}
        <div className="phase">
          <div className="phase-head">
            <span className="phase-num">3</span>
            <span className="phase-title">🔍 Self-Audit Report</span>
          </div>
          <div style={{ fontSize: 14, color: "var(--ink-2)", marginTop: 8 }}>
            {p3.summary}
          </div>
        </div>

        {/* Run again */}
        <div className="row-actions" style={{ marginTop: 24 }}>
          <button className="btn primary" onClick={onRunSleep}>
            🌙 Run Again
          </button>
        </div>
      </div>
    </div>
  );
}

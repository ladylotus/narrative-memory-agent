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
            <div className="page-title">💤 睡眠巩固日志</div>
            <div className="page-desc">
              空闲时，Agent会重放近期事件并重新组织对{shortName}的记忆——
              巩固事实、抽象模式、自我审计。
            </div>
          </div>
          <div className="empty" style={{ marginTop: 40 }}>
            <div className="e-mark">💤</div>
            <div className="e-title">还没有巩固记录</div>
            <div className="e-desc">
              运行一次睡眠巩固，Agent会分析{shortName}的所有事件，
              检测行为冲突并更新认知档案。
            </div>
            <div className="row-actions" style={{ marginTop: 20, justifyContent: "center" }}>
              <button className="btn primary" onClick={onRunSleep}>
                🌙 运行睡眠巩固
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
          <div className="page-title">💤 睡眠巩固日志</div>
          <div className="page-desc">
            对{shortName}的最新一轮记忆巩固分析
          </div>
        </div>

        {/* Summary card */}
        <div className="log-summary">
          <div className="ls-item">
            <span className="ls-k">📊 事件</span>
            <span className="ls-v">{p1.events_analyzed}</span>
          </div>
          <div className="ls-sep" />
          <div className="ls-item">
            <span className="ls-k">⚡ 冲突</span>
            <span className="ls-v" style={{ color: conflictCount > 0 ? "var(--risk-med)" : "var(--risk-low)" }}>
              {conflictCount}
            </span>
          </div>
          <div className="ls-sep" />
          <div className="ls-item">
            <span className="ls-k">🔺 加权</span>
            <span className="ls-v">{p1.importance_adjustments.length}</span>
          </div>
          <div className="ls-sep" />
          <div className="ls-item">
            <span className="ls-k">📉 置信度</span>
            <span className="ls-v" style={{ color: p3.confidence_delta < 0 ? "var(--risk-med)" : "var(--risk-low)" }}>
              {p3.confidence_delta > 0 ? "+" : ""}{p3.confidence_delta}
            </span>
          </div>
        </div>

        {/* Phase 1: 事实巩固 */}
        <div className="phase">
          <div className="phase-head">
            <span className="phase-num">1</span>
            <span className="phase-title">💤 事实巩固</span>
          </div>
          <div className="phase-sub">从事件中提取事实，检测与已知特质的矛盾</div>

          {conflictCount > 0 && (
            <div style={{ marginTop: 12, fontSize: 12, fontWeight: 600, color: "var(--risk-med)" }}>
              检测到 {conflictCount} 处行为冲突：
            </div>
          )}
          {p1.conflicts_detected.map((c, i) => (
            <div className="log-entry" key={i} style={{ borderLeft: `3px solid ${severityColor(c.severity)}` }}>
              <div style={{ fontSize: 13 }}>{c.event}</div>
              <div style={{ fontSize: 11, color: "var(--ink-3)", marginTop: 4 }}>
                <span style={{ color: severityColor(c.severity) }}>
                  {c.severity === "high" ? "🔴" : c.severity === "medium" ? "🟡" : "🟢"}
                </span>
                {" "}意图「{c.intent}」与特质「{c.conflicting_keywords.join("、")}」冲突
              </div>
            </div>
          ))}

          {p1.importance_adjustments.length > 0 && (
            <div style={{ marginTop: 12, fontSize: 12, fontWeight: 600, color: "var(--accent)" }}>
              关键事件加权调整：
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

        {/* Phase 2: 抽象整合 */}
        <div className="phase">
          <div className="phase-head">
            <span className="phase-num">2</span>
            <span className="phase-title">🧩 抽象整合</span>
          </div>
          <div className="phase-sub">提取行为模式，更新角色认知</div>

          {p2.arc_stage_change && (
            <div className="log-entry" style={{ borderLeft: "3px solid var(--accent)" }}>
              <div style={{ fontSize: 13, fontWeight: 600 }}>🔄 弧光演变</div>
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
              特质置信度调整：
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
              <span style={{ fontSize: 12 }}>✂️ 已剪枝 {p2.events_pruned} 个低权重事件</span>
            </div>
          )}
        </div>

        {/* Phase 3: 报告 */}
        <div className="phase">
          <div className="phase-head">
            <span className="phase-num">3</span>
            <span className="phase-title">🔍 自检报告</span>
          </div>
          <div style={{ fontSize: 14, color: "var(--ink-2)", marginTop: 8 }}>
            {p3.summary}
          </div>
        </div>

        {/* Run again */}
        <div className="row-actions" style={{ marginTop: 24 }}>
          <button className="btn primary" onClick={onRunSleep}>
            🌙 再跑一次
          </button>
        </div>
      </div>
    </div>
  );
}

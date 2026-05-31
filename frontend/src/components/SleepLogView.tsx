"use client";

import type { Character, SleepLog } from "@/lib/types";

export default function SleepLogView({
  char,
  log,
}: {
  char: Character;
  log: SleepLog;
}) {
  const delta = (log.confAfter - log.confBefore).toFixed(2);
  const shortName = char.name.split(" ")[0];

  return (
    <div className="scroll">
      <div className="page">
        {/* Header */}
        <div className="page-head">
          <div className="page-title">💤 睡眠巩固日志</div>
          <div className="page-desc">
            空闲时，Agent会重放近期阅读内容并重新组织对{shortName}的记忆——
            巩固事实、抽象模式、自我审计。
          </div>
        </div>

        {/* Summary */}
        <div className="log-summary">
          <div className="ls-item">
            <span className="ls-k">🔄 周期</span>
            <span className="ls-v">#{log.cycle}</span>
          </div>
          <div className="ls-sep" />
          <div className="ls-item">
            <span className="ls-k">⏰ 运行时间</span>
            <span className="ls-v">{log.ranAt}</span>
          </div>
          <div className="ls-sep" />
          <div className="ls-item">
            <span className="ls-k">⏱️ 耗时</span>
            <span className="ls-v">{log.duration}</span>
          </div>
          <div className="ls-sep" />
          <div className="ls-item">
            <span className="ls-k">📈 置信度变化</span>
            <span className="ls-v pos">+{delta}</span>
          </div>
        </div>

        {/* Phases */}
        {log.phases.map((ph) => (
          <div className="phase" key={ph.n}>
            <div className="phase-head">
              <span className="phase-num">{ph.n}</span>
              <span className="phase-title">{ph.title}</span>
            </div>
            <div className="phase-sub">{ph.sub}</div>
            {ph.entries.map((e, i) => (
              <div className="log-entry" key={i}>
                <span>{e.text}</span>
              </div>
            ))}
          </div>
        ))}

        {/* Suggestion */}
        <div className="callout">
          <span style={{ fontSize: 20 }}>✍️</span>
          <div>
            <div className="co-k">创作建议</div>
            <div className="co-body">{log.suggestion}</div>
          </div>
        </div>
      </div>
    </div>
  );
}

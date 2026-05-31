"use client";

import type { Character, CharacterProfile } from "@/lib/types";
import { NMA_NOVEL, NMA_LOG } from "@/lib/data";

function TraitBar({ pct }: { pct: number }) {
  return (
    <div className="trait-bar">
      <i style={{ width: `${pct}%` }} />
    </div>
  );
}

export default function ProfileView({
  char,
  profile,
}: {
  char: Character;
  profile?: CharacterProfile;
}) {
  if (!profile) {
    return (
      <div className="scroll">
        <div className="empty">
          <div className="e-mark">📋</div>
          <div className="e-title">{char.name} 还没有档案</div>
          <div className="e-desc">
            Agent还没有收集到足够的证据来建模{char.name.split(" ")[0]}。
            先聊几次，然后跑一个巩固周期。
          </div>
        </div>
      </div>
    );
  }

  const center = profile.relationships.find((r) => r.center);

  return (
    <div className="scroll">
      <div className="page">
        {/* Header */}
        <div className="page-head">
          <div className="page-title">🧠 认知档案</div>
          <div className="page-desc">
            Agent目前对{char.name}的认知——基于「{NMA_NOVEL.title}」，
            经过 {NMA_LOG.cycle} 次巩固周期提炼。
          </div>
        </div>

        {/* Traits */}
        <div className="sec-label">
          特质 <span className="sec-count">· {profile.traits.length}</span>
        </div>
        {profile.traits.map((t, i) => (
          <div className="trait" key={i}>
            <div className="trait-top">
              <div className="trait-name">
                {t.name}
                {t.isNew && <span className="badge-new">🆕</span>}
              </div>
              <div className="trait-conf">
                {Math.round(t.conf * 100)}%
              </div>
            </div>
            <TraitBar pct={t.conf * 100} />
            <div className="trait-evidence">
              📄 {t.evidence} 个支撑段落
            </div>
          </div>
        ))}

        {/* Relationship network */}
        <div className="sec-label">🔗 关系网络</div>
        <div className="constellation">
          <svg
            style={{ position: "absolute", inset: 0, width: "100%", height: "100%" }}
            viewBox="0 0 100 100"
            preserveAspectRatio="none"
          >
            {center &&
              profile.relationships
                .filter((r) => !r.center)
                .map((r, i) => (
                  <line
                    key={i}
                    x1={center.x}
                    y1={center.y}
                    x2={r.x}
                    y2={r.y}
                    stroke="rgba(255,255,255,0.12)"
                    strokeWidth="0.25"
                  />
                ))}
          </svg>
          {profile.relationships.map((r) => (
            <div
              key={r.id}
              className={`rel-node${r.center ? " center" : ""}`}
              style={{ left: `${r.x}%`, top: `${r.y}%` }}
            >
              <div className={`ravatar ${r.tone || ""}`}>{r.emoji}</div>
              <div className="rname">{r.name}</div>
              {!r.center && <div className="rrel">{r.rel}</div>}
            </div>
          ))}
        </div>

        {/* Behavior patterns */}
        <div className="sec-label">
          🔄 行为模式 <span className="sec-count">· {profile.patterns.length}</span>
        </div>
        {profile.patterns.map((p, i) => (
          <div className="pattern" key={i}>
            <div className="pcond">
              {p.cond} <span style={{ color: "var(--ink-4)" }}>→</span>
            </div>
            <div className="pbody">{p.body}</div>
            <div className="pstrength">
              <span className="pbars">
                {[0, 1, 2, 3].map((b) => (
                  <i key={b} className={b < p.strength ? "on" : ""} />
                ))}
              </span>
              <span className="ptext">
                {["弱", "较弱", "中等", "较强", "强"][p.strength]}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

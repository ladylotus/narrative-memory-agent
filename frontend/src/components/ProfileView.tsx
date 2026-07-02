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
  onDelete,
}: {
  char: Character;
  profile?: CharacterProfile;
  onDelete?: (name: string) => void;
}) {
  if (!profile) {
    return (
      <div className="scroll">
        <div className="empty">
          <div className="e-mark">📋</div>
          <div className="e-title">{char.name} doesn't have a profile yet</div>
          <div className="e-desc">
            The agent doesn't have enough evidence to model {char.name.split(" ")[0]}.
            Have a few conversations first, then run a consolidation cycle.
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
          <div className="page-title">🧠 Cognitive Profile</div>
          <div className="page-desc">
            The agent's current understanding of {char.name} — based on "{NMA_NOVEL.title}",
            refined over {NMA_LOG.cycle} consolidation cycles.
          </div>
        </div>

        {/* Traits */}
        <div className="sec-label">
          Traits <span className="sec-count">· {profile.traits.length}</span>
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
              📄 {t.evidence} supporting passages
            </div>
          </div>
        ))}

        {/* Relationship network */}
        <div className="sec-label">🔗 Relationship Network</div>
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
          🔄 Behavior Patterns <span className="sec-count">· {profile.patterns.length}</span>
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
                {["Weak", "Mild", "Moderate", "Strong", "Very Strong"][p.strength]}
              </span>
            </div>
          </div>
        ))}

        {/* Delete */}
        {onDelete && (
          <div style={{ marginTop: 24, paddingTop: 16, borderTop: "1px solid var(--line)" }}>
            <button
              style={{
                background: "none",
                border: "1px solid rgba(255,80,80,0.3)",
                color: "#ff5050",
                padding: "6px 14px",
                borderRadius: 6,
                fontSize: 12,
                cursor: "pointer",
                fontFamily: "inherit",
                opacity: 0.7,
              }}
              onClick={() => onDelete(char.name)}
            >
              🗑 Delete {char.name}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

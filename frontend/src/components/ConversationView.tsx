"use client";

import type { Option, Risk, Scene, Character, ConvoState, Turn } from "@/lib/types";

/* ─── RiskBadge ─── */
function RiskBadge({ risk }: { risk: Risk }) {
  return (
    <span className={`risk ${risk.level}`}>
      {risk.label} · {risk.pct}%
    </span>
  );
}

/* ─── OptionCard ─── */
function OptionCard({
  opt,
  i,
  chosen,
  anyChosen,
  onChoose,
}: {
  opt: Option;
  i: number;
  chosen: number | null;
  anyChosen: boolean;
  onChoose: (i: number) => void;
}) {
  const isChosen = chosen === i;
  const cls = `opt${isChosen ? " chosen" : ""}${anyChosen && !isChosen ? " dimmed" : ""}`;
  return (
    <div className={cls} onClick={() => onChoose(i)}>
      <div className="opt-head">
        <span className="opt-idx">{opt.idx}</span>
        <RiskBadge risk={opt.risk} />
      </div>
      <div className="opt-title">{opt.title}</div>
      <div className="opt-voice">{opt.voice}</div>
      <div className="opt-foot">
        <span>{opt.tagNew ? "🆕" : "🏷️"}</span>
        <span style={{ fontSize: 12, color: "var(--ink-3)" }}>{opt.tag}</span>
      </div>
    </div>
  );
}

/* ─── FeedbackBar ─── */
function FeedbackBar({
  characterName,
  feedback,
  note,
  submitted,
  onFeedback,
  onNote,
  onSubmit,
}: {
  characterName: string;
  feedback: string | null;
  note: string;
  submitted: boolean;
  onFeedback: (v: string) => void;
  onNote: (v: string) => void;
  onSubmit: () => void;
}) {
  if (submitted) {
    return (
      <div className="feedback fadein">
        <div className="fb-done" style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 13, color: "var(--risk-low)" }}>
          ✅ 已存入记忆 · 将在今晚的巩固周期中处理
        </div>
      </div>
    );
  }

  return (
    <div className="feedback fadein">
      <div className="fb-q">🎯 像{characterName}吗？</div>
      <div className="fb-opts">
        {[
          { v: "fits", label: "✅ 很像" },
          { v: "drift", label: "⚠️ 有点偏" },
          { v: "off", label: "❌ 完全不像" },
        ].map((o) => (
          <button
            key={o.v}
            className={`fb-btn${feedback === o.v ? " sel" : ""}`}
            onClick={() => onFeedback(o.v)}
          >
            {o.label}
          </button>
        ))}
      </div>
      <div className="fb-note">
        <textarea
          placeholder="可选——写下你的想法，这将成为记忆的一部分。"
          value={note}
          onChange={(e) => onNote(e.target.value)}
        />
      </div>
      <div className="row-actions">
        <button className="btn primary" disabled={!feedback} onClick={onSubmit}>
          💾 存入记忆
        </button>
      </div>
    </div>
  );
}

/* ─── ConversationView ─── */
export default function ConversationView({
  char,
  scene,
  options,
  convo,
  actions,
  hasContent,
}: {
  char: Character;
  scene: Scene;
  options: Option[];
  convo: ConvoState;
  actions: {
    onChoose: (i: number) => void;
    onFeedback: (v: string) => void;
    onNote: (v: string) => void;
    onSubmit: () => void;
    onSend: (text: string) => void;
  };
  hasContent: boolean;
}) {
  const shortName = char.name.split(" ")[0];

  if (!hasContent) {
    return (
      <div className="scroll">
        <div className="empty">
          <div className="e-mark">🎭</div>
          <div className="e-title">{char.name} 还在成形中</div>
          <div className="e-desc">
            置信度 {Math.round(char.confidence * 100)}%。问{shortName}一个问题，
            每次回答和你的反馈都会进入下一次巩固周期。
          </div>
        </div>
        <Composer shortName={shortName} onSend={actions.onSend} />
      </div>
    );
  }

  const anyChosen = convo.chosen !== null && convo.chosen !== undefined;

  return (
    <div className="scroll">
      <div className="convo">
        {/* Scene card */}
        <div className="scene-card">
          <div className="scene-eyebrow">{scene.eyebrow}</div>
          <div className="scene-text">{scene.text}</div>
          <span className="scene-q">{scene.question}</span>
        </div>

        {/* Turn label */}
        <div className="turn-label">
          🎭 {options.length} 个发展方向，按契合度排序
        </div>

        {/* Options */}
        <div className="options">
          {options.map((opt, i) => (
            <OptionCard
              key={i}
              opt={opt}
              i={i}
              chosen={convo.chosen}
              anyChosen={anyChosen}
              onChoose={actions.onChoose}
            />
          ))}
        </div>

        {/* Feedback */}
        {anyChosen && (
          <FeedbackBar
            characterName={shortName}
            feedback={convo.feedback}
            note={convo.note}
            submitted={convo.submitted}
            onFeedback={actions.onFeedback}
            onNote={actions.onNote}
            onSubmit={actions.onSubmit}
          />
        )}

        {/* Follow-up turns */}
        {convo.turns.map((t, ti) => (
          <div key={ti}>
            <div className="user-turn fadein">
              <div className="user-bubble">{t.text}</div>
            </div>
            {t.options && (
              <>
                <div className="turn-label">
                  🎭 {t.options.length} 个方向
                </div>
                <div className="options">
                  {t.options.map((opt, i) => (
                    <OptionCard
                      key={i}
                      opt={opt}
                      i={i}
                      chosen={null}
                      anyChosen={false}
                      onChoose={() => {}}
                    />
                  ))}
                </div>
              </>
            )}
          </div>
        ))}

        {/* Thinking indicator */}
        {convo.thinking && (
          <div className="thinking fadein">
            <span className="pulse"><i /><i /><i /></span>
            🔮 正在读取{shortName}的记忆…
          </div>
        )}
      </div>

      <Composer shortName={shortName} onSend={actions.onSend} />
    </div>
  );
}

/* ─── Composer ─── */
function Composer({
  shortName,
  onSend,
}: {
  shortName: string;
  onSend: (text: string) => void;
}) {
  return (
    <div className="composer-wrap">
      <div className="composer">
        <div className="composer-inner">
          <textarea
            rows={1}
            placeholder={`💬 Describe a scene, or ask ${shortName} what they would do…`}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                const el = e.currentTarget;
                if (el.value.trim()) {
                  onSend(el.value.trim());
                  el.value = "";
                }
              }
            }}
          />
          <button
            className="send-btn"
            onClick={(e) => {
              const el = e.currentTarget.parentElement?.querySelector("textarea");
              if (el && el.value.trim()) {
                onSend(el.value.trim());
                el.value = "";
              }
            }}
          >
            如果是你，你会？
          </button>
        </div>
      </div>
    </div>
  );
}

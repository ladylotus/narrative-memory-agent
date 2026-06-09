"use client";

import { useEffect } from "react";
import type { Option, Risk, Scene, Character, ConvoState, Turn } from "@/lib/types";

/* ─── Mark options ─────────────────────────── */
const MARK_OPTIONS = [
  { value: "这就是他会做的事", label: "这就是他会做的事", icon: "🎯" },
  { value: "情节需要这个走向", label: "情节需要这个走向", icon: "📜" },
  { value: "想看看这个可能性", label: "想看看这个可能性", icon: "🔮" },
  { value: "说不上来，就是感觉", label: "说不上来，就是感觉", icon: "🤔" },
] as const;

/* ─── RiskBadge ─── */
function RiskBadge({ risk }: { risk: Risk }) {
  let cls = `risk ${risk.level}`;
  if (risk.type === "surprise") cls += " surprise";
  return (
    <span className={cls}>
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
  marks,
  note,
  submitted,
  onToggleMark,
  onNote,
  onSubmit,
}: {
  characterName: string;
  marks: string[];
  note: string;
  submitted: boolean;
  onToggleMark: (v: string) => void;
  onNote: (v: string) => void;
  onSubmit: () => void;
}) {
  if (submitted) {
    return (
      <div className="feedback fadein">
        <div className="fb-done" style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 13, color: "var(--risk-low)" }}>
          ✅ 已存入记忆 · 将在下次生成中参考你的偏好
        </div>
      </div>
    );
  }

  return (
    <div className="feedback fadein">
      <div className="fb-q">💡 你选这个是因为……？</div>
      <div className="fb-marks">
        {MARK_OPTIONS.map((o) => {
          const sel = marks.includes(o.value);
          return (
            <button
              key={o.value}
              className={`fb-mark${sel ? " sel" : ""}`}
              onClick={() => onToggleMark(o.value)}
            >
              {sel ? "☑" : "□"} {o.label}
            </button>
          );
        })}
      </div>
      <div className="fb-note">
        <textarea
          placeholder="可选——写下你的想法，这将成为记忆的一部分。"
          value={note}
          onChange={(e) => onNote(e.target.value)}
        />
      </div>
      <div className="row-actions">
        <button className="btn primary" disabled={marks.length === 0} onClick={onSubmit}>
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
  feedbackPreference = "always",
}: {
  char: Character;
  scene: Scene;
  options: Option[];
  convo: ConvoState;
  actions: {
    onChoose: (i: number) => void;
    onToggleMark: (v: string) => void;
    onNote: (v: string) => void;
    onSubmit: () => void;
    onSend: (text: string) => void;
  };
  hasContent: boolean;
  feedbackPreference?: "always" | "on-ooc" | "never";
}) {
  const shortName = char.name.split(" ")[0];

  // Auto-submit based on feedback preference
  const shouldAutoSubmit =
    feedbackPreference === "never" ||
    (feedbackPreference === "on-ooc" &&
      convo.chosen !== null &&
      !convo.submitted &&
      options[convo.chosen]?.risk.level !== "high");

  useEffect(() => {
    if (shouldAutoSubmit && !convo.submitted) {
      const timer = setTimeout(() => actions.onSubmit(), 400);
      return () => clearTimeout(timer);
    }
  }, [shouldAutoSubmit, convo.submitted, actions]);

  const showFeedback =
    convo.chosen !== null &&
    !convo.submitted &&
    !shouldAutoSubmit;

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
        {showFeedback && (
          <FeedbackBar
            characterName={shortName}
            marks={convo.marks}
            note={convo.note}
            submitted={convo.submitted}
            onToggleMark={actions.onToggleMark}
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

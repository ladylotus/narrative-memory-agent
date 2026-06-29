"use client";

import { useEffect, useState } from "react";
import type { Option, Risk, Scene, Character, ConvoState, Turn } from "@/lib/types";

/* ─── Mark options ─────────────────────────── */
const MARK_OPTIONS = [
  { value: "role-driven", label: "It's what they'd do", icon: "🎯" },
  { value: "plot-driven", label: "The plot needs this", icon: "📜" },
  { value: "experimental", label: "Curious about this path", icon: "🔮" },
  { value: "gut-feeling", label: "Just feels right", icon: "🤔" },
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
          ✅ Saved to memory · Your preference will guide future generations
        </div>
      </div>
    );
  }

  return (
    <div className="feedback fadein">
      <div className="fb-q">💡 Why did you choose this?</div>
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
          placeholder="Optional — your notes become part of memory."
          value={note}
          onChange={(e) => onNote(e.target.value)}
        />
      </div>
      <div className="row-actions">
        <button className="btn primary" disabled={marks.length === 0} onClick={onSubmit}>
          💾 Save to Memory
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
  resumeStatus = null,
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
  resumeStatus?: { has_resumed: boolean; turn_count: number; last_question: string } | null;
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
        {resumeStatus?.has_resumed && (
          <div className="resume-banner fadein">
            🔁 Welcome back — {resumeStatus.turn_count} previous exchanges remembered.
            {resumeStatus.last_question && <> Last topic: <em>"{resumeStatus.last_question.slice(0, 80)}"</em></>}
          </div>
        )}
        <div className="empty">
          <div className="e-mark">🎭</div>
          <div className="e-title">{char.name} is still taking shape</div>
          <div className="e-desc">
            {Math.round(char.confidence * 100)}% confidence. Ask {shortName} a question — every answer and your feedback feeds the next consolidation cycle.
          </div>
        </div>
        <Composer shortName={shortName} onSend={actions.onSend} />
      </div>
    );
  }

  const anyChosen = convo.chosen !== null && convo.chosen !== undefined;

  return (
    <div className="scroll">
      {resumeStatus?.has_resumed && (
        <div className="resume-banner fadein">
          🔁 Welcome back — {resumeStatus.turn_count} previous exchanges remembered.
          {resumeStatus.last_question && <> Last topic: <em>"{resumeStatus.last_question.slice(0, 80)}"</em></>}
        </div>
      )}

      <div className="convo">
        {/* Arc banner — compact character intro, replaces the big scene card */}
        {scene && options.length === 0 && convo.turns.filter(t => t.options).length === 0 && !convo.thinking && (
          <div className="arc-banner fadein">
            <span className="arc-banner-icon">{char.emoji}</span>
            <span className="arc-banner-text">
              {char.name} · {scene.text}
            </span>
          </div>
        )}

        {/* Completed turns — history with character responses */}
        {convo.turns.filter(t => t.options).map((t, ti) => (
          <TurnHistory key={ti} turn={t} turnIndex={ti} characterName={char.name} />
        ))}

        {/* Current exchange — the last turn without options yet */}
        {(() => {
          const lastTurn = convo.turns.length > 0 ? convo.turns[convo.turns.length - 1] : null;
          if (!lastTurn || lastTurn.options) return null;

          return (
            <>
              {/* User message */}
              <div className="user-turn fadein">
                <div className="user-bubble">{lastTurn.text}</div>
              </div>

              {/* Options */}
              {!convo.thinking && options.length > 0 && (
                <>
                  <div className="turn-label">
                    🎭 {options.length} paths, sorted by likelihood
                  </div>
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
                </>
              )}

              {/* Chosen option — character response inline */}
              {convo.chosen !== null && options[convo.chosen] && (
                <div className="chosen-response-section fadein">
                  <div className="char-response">
                    <div className="char-response-name">{shortName}</div>
                    <div className="char-response-text">{options[convo.chosen].voice}</div>
                  </div>
                </div>
              )}
            </>
          );
        })()}

        {/* Thinking indicator */}
        {convo.thinking && (
          <ThinkingAnimation shortName={shortName} />
        )}
      </div>

      {/* Footer: feedback + composer */}
      <div className="convo-footer">
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
        <Composer shortName={shortName} onSend={actions.onSend} />
      </div>
    </div>
  );
}

/* ─── ThinkingAnimation ─── */
const THOUGHTS: Record<string, string[]> = {
  "Elizabeth": [
    "Elizabeth turns your question over in her mind…",
    "She recalls the spark in dark eyes at Netherfield…",
    "A memory of Hertfordshire lanes flickers past…",
    "She weighs wit against discretion…",
    "Her fingers trace the spine of a well-read book…",
    "She looks out the window, composing her thoughts…",
    "A half-smile forms as she considers her answer…",
  ],
  "Darcy": [
    "Darcy pauses to gather his words…",
    "He reflects on matters of honour and feeling…",
    "The memory of a rainy proposal surfaces…",
    "He straightens his coat, unsettled…",
    "Pemberley's halls echo in his recollection…",
    "He wrestles with pride and something softer…",
    "His gaze steadies as he prepares to speak…",
  ],
};

const FALLBACK_THOUGHTS = [
  "Turning pages of memory…",
  "Searching for the right words…",
  "A story unfolds in quiet thought…",
];

function ThinkingAnimation({ shortName }: { shortName: string }) {
  const [idx, setIdx] = useState(0);
  const pool = THOUGHTS[shortName] ?? FALLBACK_THOUGHTS;

  useEffect(() => {
    const timer = setInterval(() => {
      setIdx((p) => (p + 1) % pool.length);
    }, 2500);
    return () => clearInterval(timer);
  }, [pool.length]);

  return (
    <div className="thinking-anim fadein">
      <div className="thinking-anim-icon">
        <span className="ta-quill">✧</span>
      </div>
      <div className="thinking-anim-text" key={idx}>
        {pool[idx]}
      </div>
    </div>
  );
}

/* ─── TurnHistory — a single past exchange ─── */
function TurnHistory({
  turn,
  turnIndex,
  characterName,
}: {
  turn: { text: string; options: Option[]; chosen: number | null };
  turnIndex: number;
  characterName: string;
}) {
  const [showOtherOptions, setShowOtherOptions] = useState(false);
  const shortName = characterName.split(" ")[0];

  // No saved options — user message only (still loading or initial state)
  if (!turn.options || turn.options.length === 0) {
    return (
      <div className="user-turn fadein">
        <div className="user-bubble">{turn.text}</div>
      </div>
    );
  }

  const chosenOpt = turn.chosen !== null ? turn.options[turn.chosen] : null;
  const otherOptions = turn.chosen !== null
    ? turn.options.filter((_, i) => i !== turn.chosen)
    : turn.options;

  return (
    <div className="turn-history-block fadein">
      {/* User message */}
      <div className="user-turn">
        <div className="user-bubble">{turn.text}</div>
      </div>

      {/* Character's response bubble — shows voice text directly */}
      {chosenOpt && (
        <div className="char-response">
          <div className="char-response-head">
            <span className="char-response-name">{shortName}</span>
            <span className={`char-response-badge ${chosenOpt.risk.level}`}>{chosenOpt.tag} · {chosenOpt.risk.pct}%</span>
          </div>
          <div className="char-response-text">{chosenOpt.voice}</div>
        </div>
      )}

      {/* Toggle for other (unchosen) options */}
      {otherOptions.length > 1 && (
        <div className="other-options-section">
          <button
            className="toggle-other-btn"
            onClick={() => setShowOtherOptions(!showOtherOptions)}
          >
            {showOtherOptions
              ? "▾ Hide other options"
              : `▸ 查看其他选项 (${otherOptions.length})`}
          </button>
          {showOtherOptions && (
            <div className="options other-options-list">
              {otherOptions.map((opt, i) => (
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
          )}
        </div>
      )}
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
  function autoResize(el: HTMLTextAreaElement) {
    el.style.height = "auto";
    el.style.height = Math.min(el.scrollHeight, 120) + "px";
  }
  return (
    <div className="composer-wrap">
      <div className="composer">
        <div className="composer-inner">
          <textarea
            placeholder={`💬 Describe a scene, or ask ${shortName} what they would do…`}
            onInput={(e) => autoResize(e.currentTarget)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                const el = e.currentTarget;
                if (el.value.trim()) {
                  onSend(el.value.trim());
                  el.value = "";
                  el.style.height = "auto";
                }
              }
            }}
          />
          <button
            className="send-btn"
            onClick={(e) => {
              const ta = e.currentTarget.parentElement?.querySelector("textarea");
              if (ta && ta.value.trim()) {
                onSend(ta.value.trim());
                ta.value = "";
                ta.style.height = "auto";
              }
            }}
          >
            What would you do?
          </button>
        </div>
      </div>
    </div>
  );
}

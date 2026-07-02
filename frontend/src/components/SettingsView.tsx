"use client";

import type { Novel } from "@/lib/types";

const OPTIONS = [
  { value: 'always', label: 'After every pick', desc: 'Ask for reasoning after every choice' },
  { value: 'on-ooc', label: 'High-risk only', desc: 'Only ask when a choice has elevated OOC risk' },
  { value: 'never', label: 'Never', desc: 'Auto-record preferences, no popups' },
] as const;

export default function SettingsView({
  novel,
  feedbackPreference,
  onChangeFeedbackPreference,
  onNavigate,
}: {
  novel: Novel;
  feedbackPreference: "always" | "on-ooc" | "never";
  onChangeFeedbackPreference: (v: "always" | "on-ooc" | "never") => void;
  onNavigate?: (view: string) => void;
}) {
  return (
    <div className="scroll">
      <div className="page">
        <div className="page-head">
          <div className="page-title">⚙️ Settings</div>
          <div className="page-desc">Manage your source text and preferences.</div>
        </div>

        <div className="settings-group">
          {/* Novel info */}
          <div className="settings-row">
            <div className="settings-label">
              <span className="sl-name">
                {novel.emoji} {novel.title}
              </span>
              <span className="sl-desc">
                {novel.author} · {novel.year} · {novel.chapters} chapters
              </span>
            </div>
          </div>

          {/* Import */}
          <div className="settings-row">
            <div className="settings-label">
              <span className="sl-name">📤 Import New Text</span>
              <span className="sl-desc">Upload a .txt file or paste chapter content</span>
            </div>
            <button className="btn primary" onClick={() => onNavigate?.("ingestion")}>Import</button>
          </div>

          {/* Model */}
          <div className="settings-row">
            <div className="settings-label">
              <span className="sl-name">🤖 Model</span>
              <span className="sl-desc">Qwen model · 1M tokens remaining</span>
            </div>
          </div>

          {/* Theme accent */}
          <div className="settings-row">
            <div className="settings-label">
              <span className="sl-name">🎨 Theme</span>
              <span className="sl-desc">Only OOC risk colors remain; everything else is monochrome</span>
            </div>
          </div>

          {/* Generation Bias — feedback preference */}
          <div className="settings-divider" />

          <div className="settings-row">
            <div className="settings-label">
              <span className="sl-name">🎯 Feedback Preference</span>
              <span className="sl-desc">
                When to ask for feedback after a choice, helping the AI learn your criteria
              </span>
            </div>
          </div>

          {OPTIONS.map((opt) => {
            const sel = feedbackPreference === opt.value;
            return (
              <label
                key={opt.value}
                className={`toggle-row${sel ? " active" : ""}`}
              >
                <input
                  type="radio"
                  name="feedbackPreference"
                  value={opt.value}
                  checked={sel}
                  onChange={() => onChangeFeedbackPreference(opt.value)}
                />
                <span className="toggle-knob">
                  <span className="tk-dot" />
                </span>
                <div className="toggle-label">
                  <span className="tl-name">{opt.label}</span>
                  <span className="tl-desc">{opt.desc}</span>
                </div>
              </label>
            );
          })}
        </div>
      </div>
    </div>
  );
}

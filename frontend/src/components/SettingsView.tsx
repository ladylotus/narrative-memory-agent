"use client";

import type { Novel } from "@/lib/types";

const OPTIONS = [
  { value: "always", label: "每次选择后", desc: "每次选了选项都会弹窗问原因" },
  { value: "on-ooc", label: "仅高风险时", desc: "仅当选项有较高OOC风险时才询问" },
  { value: "never", label: "不询问", desc: "自动记录偏好，不会弹窗" },
] as const;

export default function SettingsView({
  novel,
  feedbackPreference,
  onChangeFeedbackPreference,
}: {
  novel: Novel;
  feedbackPreference: "always" | "on-ooc" | "never";
  onChangeFeedbackPreference: (v: "always" | "on-ooc" | "never") => void;
}) {
  return (
    <div className="scroll">
      <div className="page">
        <div className="page-head">
          <div className="page-title">⚙️ 设置</div>
          <div className="page-desc">管理你的源文本和偏好。</div>
        </div>

        <div className="settings-group">
          {/* Novel info */}
          <div className="settings-row">
            <div className="settings-label">
              <span className="sl-name">
                {novel.emoji} {novel.title}
              </span>
              <span className="sl-desc">
                {novel.author} · {novel.year} · {novel.chapters} 章
              </span>
            </div>
          </div>

          {/* Import */}
          <div className="settings-row">
            <div className="settings-label">
              <span className="sl-name">📤 导入新文本</span>
              <span className="sl-desc">上传 .txt 文件或粘贴章节内容</span>
            </div>
            <button className="btn primary">导入</button>
          </div>

          {/* Model */}
          <div className="settings-row">
            <div className="settings-label">
              <span className="sl-name">🤖 模型</span>
              <span className="sl-desc">qwen3.6-plus · 1M tokens 剩余</span>
            </div>
          </div>

          {/* Theme accent */}
          <div className="settings-row">
            <div className="settings-label">
              <span className="sl-name">🎨 主题</span>
              <span className="sl-desc">只保留OOC风险色，其他全单色</span>
            </div>
          </div>

          {/* Generation Bias — feedback preference */}
          <div className="settings-divider" />

          <div className="settings-row">
            <div className="settings-label">
              <span className="sl-name">🎯 偏好询问</span>
              <span className="sl-desc">
                选择后何时询问反馈，帮助AI学习你的判断标准
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

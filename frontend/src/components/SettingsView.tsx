"use client";

import type { Novel } from "@/lib/types";

export default function SettingsView({ novel }: { novel: Novel }) {
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
        </div>
      </div>
    </div>
  );
}

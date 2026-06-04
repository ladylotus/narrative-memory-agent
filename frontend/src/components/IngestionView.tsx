"use client";

import { useState } from "react";
import { ingestNovel } from "@/lib/api";
import type { IngestResult } from "@/lib/api";

export default function IngestionView({
  onCharactersCreated,
}: {
  onCharactersCreated: () => void;
}) {
  const [text, setText] = useState("");
  const [title, setTitle] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<IngestResult | null>(null);
  const [error, setError] = useState("");

  const handleAnalyze = async () => {
    if (!text.trim()) return;
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const res = await ingestNovel(text.trim(), title || undefined);
      setResult(res);
      onCharactersCreated();
    } catch (e) {
      setError(String(e));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="scroll">
      <div className="page">
        <div className="page-head">
          <div className="page-title">📖 阅读室</div>
          <div className="page-desc">
            贴入小说文本，我会分析角色、事件和关系，构建三层记忆。
          </div>
        </div>

        {/* Text input */}
        <div className="settings-group" style={{ marginTop: 24 }}>
          <div className="settings-row" style={{ flexDirection: "column", gap: 8, alignItems: "stretch" }}>
            <div className="settings-label">
              <span className="sl-name">标题（可选）</span>
            </div>
            <input
              className="ingest-input"
              placeholder="e.g. Seen — Chapter 1"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
            />
          </div>

          <div className="settings-row" style={{ flexDirection: "column", gap: 8, alignItems: "stretch" }}>
            <div className="settings-label">
              <span className="sl-name">小说文本</span>
              <span className="sl-desc">
                粘贴章节内容或完整片段
              </span>
            </div>
            <textarea
              className="ingest-textarea"
              placeholder={`Paste your novel text here…\n\nExample:\nMaren had been dead for three months, and I still reached for her voice every time the kitchen started burning.\n\n"Move the venison off the fire. Now."`}
              rows={12}
              value={text}
              onChange={(e) => setText(e.target.value)}
            />
          </div>

          <div className="settings-row" style={{ justifyContent: "flex-end", paddingTop: 4 }}>
            <button
              className="btn primary"
              disabled={!text.trim() || loading}
              onClick={handleAnalyze}
            >
              {loading ? "🔮 分析中…" : "📥 摄入并分析"}
            </button>
          </div>
        </div>

        {/* Error */}
        {error && (
          <div className="ingest-error fadein">
            ❌ {error}
          </div>
        )}

        {/* Results */}
        {result && (
          <div className="ingest-result fadein">
            <div className="ir-head">✅ 分析完成</div>
            <div className="ir-stats">
              <div className="ir-stat">
                <span className="ir-n">{result.chunks_processed}</span>
                <span className="ir-l">文本块</span>
              </div>
              <div className="ir-stat">
                <span className="ir-n">{result.events_extracted}</span>
                <span className="ir-l">事件</span>
              </div>
              <div className="ir-stat">
                <span className="ir-n">{result.characters_found.length}</span>
                <span className="ir-l">角色</span>
              </div>
              {result.new_characters.length > 0 && (
                <div className="ir-stat">
                  <span className="ir-n ir-new">+{result.new_characters.length}</span>
                  <span className="ir-l">新角色</span>
                </div>
              )}
            </div>

            {result.characters_found.length > 0 && (
              <div className="ir-chars">
                <div className="ir-sub">识别的角色：</div>
                <div className="ir-tags">
                  {result.characters_found.map((name) => (
                    <span
                      key={name}
                      className={`ir-tag${result.new_characters.includes(name) ? " new" : ""}`}
                    >
                      {result.new_characters.includes(name) ? "🆕 " : "📄 "}
                      {name}
                    </span>
                  ))}
                </div>
              </div>
            )}

            <div className="ir-foot">
              <span>→ 前往 <strong>💬 对话</strong> 标签页与角色交流</span>
            </div>
          </div>
        )}

        {/* Loading state */}
        {loading && (
          <div className="ingest-thinking fadein">
            <span className="pulse"><i /><i /><i /></span>
            <span>🔮 正在阅读文本，提取角色和事件…</span>
          </div>
        )}
      </div>
    </div>
  );
}

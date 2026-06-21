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
      const detail = e instanceof Error ? e.message : String(e);
      setError(
        detail.length > 120 ? detail.slice(0, 120) + "…" : detail
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="scroll">
      <div className="page">
        <div className="page-head">
          <div className="page-title">📖 Reading Room</div>
          <div className="page-desc">
            Paste novel text — I'll analyze characters, events, and relationships, then build a three-layer memory.
          </div>
        </div>

        {/* Text input */}
        <div className="settings-group" style={{ marginTop: 24 }}>
          <div className="settings-row" style={{ flexDirection: "column", gap: 8, alignItems: "stretch" }}>
            <div className="settings-label">
              <span className="sl-name">Title (optional)</span>
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
              <span className="sl-name">Novel Text</span>
              <span className="sl-desc">
                Paste chapter content or a full excerpt
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
              {loading ? "🔮 Analyzing…" : "📥 Ingest & Analyze"}
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
            <div className="ir-head">✅ Analysis Complete</div>
            <div className="ir-stats">
              <div className="ir-stat">
                <span className="ir-n">{result.chunks_processed}</span>
                <span className="ir-l">chunks</span>
              </div>
              <div className="ir-stat">
                <span className="ir-n">{result.events_extracted}</span>
                <span className="ir-l">events</span>
              </div>
              <div className="ir-stat">
                <span className="ir-n">{result.characters_found.length}</span>
                <span className="ir-l">characters</span>
              </div>
              {result.new_characters.length > 0 && (
                <div className="ir-stat">
                  <span className="ir-n ir-new">+{result.new_characters.length}</span>
                  <span className="ir-l">new</span>
                </div>
              )}
            </div>

            {result.characters_found.length > 0 && (
              <div className="ir-chars">
                <div className="ir-sub">Characters identified:</div>
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
              <span>→ Go to <strong>💬 Chat</strong> to talk with characters</span>
            </div>
          </div>
        )}

        {/* Loading state */}
        {loading && (
          <div className="ingest-thinking fadein">
            <span className="pulse"><i /><i /><i /></span>
            <span>🔮 Reading text, extracting characters and events…</span>
          </div>
        )}
      </div>
    </div>
  );
}

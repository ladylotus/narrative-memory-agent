"use client";

import type { Character, Novel } from "@/lib/types";

interface SidebarProps {
  characters: Character[];
  activeChar: string;
  novel: Novel;
  view: string;
  onSelectChar: (id: string) => void;
  onNav: (view: string) => void;
}

export default function Sidebar({
  characters,
  activeChar,
  novel,
  view,
  onSelectChar,
  onNav,
}: SidebarProps) {
  return (
    <aside className="sidebar">
      {/* Brand */}
      <div className="brand">
        <div className="brand-mark">📖</div>
        <div>
          <div className="brand-name">Narrative Memory</div>
          <div className="brand-sub">Agent</div>
        </div>
      </div>

      {/* Novel chip */}
      <div className="novel-chip" onClick={() => onNav("settings")}>
        <span>{novel.emoji}</span>
        <div className="nc-meta">
          <div className="nc-title">{novel.title}</div>
          <div className="nc-sub">
            {characters.length} characters · {novel.chapters} chapters
          </div>
        </div>
      </div>

      {/* Character list */}
      <div className="side-label">Characters</div>
      <div className="char-list">
        {characters.map((c) => (
          <div
            key={c.id}
            className={`char-row${
              c.id === activeChar && view !== "settings" ? " active" : ""
            }`}
            onClick={() => onSelectChar(c.id)}
          >
            <div className="avatar">{c.emoji}</div>
            <div className="char-meta">
              <div className="char-name">{c.name}</div>
              <div className="char-status">
                {c.flag ? (
                  <>{c.flag}</>
                ) : c.status === "forming" ? (
                  <>🌱 Forming · {Math.round(c.confidence * 100)}%</>
                ) : (
                  <>🧠 {Math.round(c.confidence * 100)}% confidence</>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Footer actions */}
      <div className="side-foot">
        <button className="side-action" onClick={() => onNav("ingestion")}>
          📤 Import Text
        </button>
        <button
          className={`side-action${view === "settings" ? " active" : ""}`}
          onClick={() => onNav("settings")}
        >
          ⚙️ Settings
        </button>
      </div>
    </aside>
  );
}

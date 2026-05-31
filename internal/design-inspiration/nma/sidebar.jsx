/* Sidebar — wordmark, novel chip, character list, footer actions */
function Sidebar({ characters, activeChar, onSelectChar, view, onNav, novel }) {
  const Icon = window.Icon;
  return (
    <aside className="sidebar">
      <div className="brand">
        <div className="brand-mark" />
        <div>
          <div className="brand-name">Narrative Memory</div>
          <div className="brand-sub">Agent</div>
        </div>
      </div>

      <div className="novel-chip" onClick={() => onNav("settings")} title="Manage source text">
        <Icon name="book" size={16} />
        <div className="nc-meta">
          <div className="nc-title">{novel.title}</div>
          <div className="nc-sub">{characters.length} characters · {novel.chapters} ch.</div>
        </div>
      </div>

      <div className="side-label">Characters</div>
      <div className="char-list">
        {characters.map((c) => (
          <div
            key={c.id}
            className={"char-row" + (c.id === activeChar && view !== "settings" ? " active" : "")}
            onClick={() => onSelectChar(c.id)}
          >
            <div className="avatar">{c.monogram}</div>
            <div className="char-meta">
              <div className="char-name">{c.name}</div>
              <div className={"char-status " + c.status}>
                <span className="dot" />
                {c.flag
                  ? c.flag
                  : c.status === "forming"
                    ? "Memory forming · " + c.confidence.toFixed(2)
                    : "Confidence " + c.confidence.toFixed(2)}
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="side-foot">
        <button className="side-action" onClick={() => onNav("settings")}>
          <Icon name="upload" size={16} /> Import text
        </button>
        <button
          className={"side-action" + (view === "settings" ? " active" : "")}
          onClick={() => onNav("settings")}
        >
          <Icon name="settings" size={16} /> Settings
        </button>
      </div>
    </aside>
  );
}

Object.assign(window, { Sidebar });

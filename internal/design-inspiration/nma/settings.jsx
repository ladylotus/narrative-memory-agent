/* Settings / Import — source text management + memory preferences */
function SettingsView({ novel }) {
  const Icon = window.Icon;
  const [cadence, setCadence] = React.useState("nightly");
  const [paste, setPaste] = React.useState("");

  return (
    <div className="scroll">
      <div className="page">
        <div className="page-head">
          <div className="page-title">Source &amp; settings</div>
          <div className="page-desc">
            One manuscript at a time. The agent extracts its cast, then builds a memory of
            each character as you read and converse.
          </div>
        </div>

        <div className="sec-label">Current source</div>
        <div className="source-card">
          <div className="sc-cover" />
          <div style={{ flex: 1 }}>
            <div className="sc-title">{novel.title}</div>
            <div className="sc-meta">
              {novel.author} · {novel.year} · {novel.words.toLocaleString()} words · {novel.chapters} chapters
            </div>
          </div>
          <button className="btn">
            <Icon name="refresh" size={14} /> Re-extract cast
          </button>
        </div>

        <div className="sec-label">Replace source</div>
        <div className="field">
          <div className="field-label">Paste manuscript</div>
          <div className="field-help">Plain text. The agent will re-read from chapter one and rebuild every dossier.</div>
          <textarea
            className="paste-area"
            placeholder="Paste your novel here…"
            value={paste}
            onChange={(e) => setPaste(e.target.value)}
          />
          <div className="row-actions">
            <button className="btn"><Icon name="upload" size={14} /> Upload .txt</button>
            <button className="btn primary" disabled={!paste.trim()}>
              <Icon name="arrow" size={14} /> Extract characters
            </button>
          </div>
        </div>

        <div className="sec-label">Memory</div>
        <div className="field">
          <div className="field-label">Consolidation cadence</div>
          <div className="field-help">When the agent replays reading and re-organises character memory.</div>
          <div className="seg">
            {[["nightly", "Nightly"], ["chapter", "After each chapter"], ["manual", "On demand"]].map(([v, l]) => (
              <button key={v} className={cadence === v ? "on" : ""} onClick={() => setCadence(v)}>{l}</button>
            ))}
          </div>
        </div>

        <div className="field">
          <div className="field-label">Appearance</div>
          <div className="field-help">
            Open the Tweaks panel from the toolbar to change accent colour, density, and the
            character-voice display on option cards.
          </div>
        </div>
      </div>
    </div>
  );
}

Object.assign(window, { SettingsView });

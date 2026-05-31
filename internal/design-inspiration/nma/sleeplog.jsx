/* Sleep Consolidation Log — three-phase memory processing report */
function SleepLogView({ char, log }) {
  const Icon = window.Icon;
  const delta = (log.confAfter - log.confBefore).toFixed(2);

  return (
    <div className="scroll">
      <div className="page">
        <div className="page-head">
          <div className="page-title">Sleep consolidation log</div>
          <div className="page-desc">
            While idle, the agent replays recent reading and re-organises its memory of {char.name.split(" ")[0]} —
            consolidating facts, abstracting patterns, and auditing itself.
          </div>
        </div>

        <div className="log-summary">
          <div className="ls-item">
            <span className="ls-k">Cycle</span>
            <span className="ls-v">#{log.cycle}</span>
          </div>
          <div className="ls-sep" />
          <div className="ls-item">
            <span className="ls-k">Ran at</span>
            <span className="ls-v">{log.ranAt}</span>
          </div>
          <div className="ls-sep" />
          <div className="ls-item">
            <span className="ls-k">Duration</span>
            <span className="ls-v">{log.duration}</span>
          </div>
          <div className="ls-sep" />
          <div className="ls-item">
            <span className="ls-k">Confidence</span>
            <span className="ls-v pos">+{delta}</span>
          </div>
        </div>

        {log.phases.map((ph) => (
          <div className="phase" key={ph.n}>
            <div className="phase-head">
              <span className="phase-num">{ph.n}</span>
              <span className="phase-title">Phase {ph.n} — {ph.title}</span>
            </div>
            <div className="phase-sub">{ph.sub}</div>
            {ph.entries.map((e, i) => (
              <div className="log-entry" key={i}>
                <span className={"le-tag " + e.tag.replace(" ", "-")}>{e.tag}</span>
                <span className="le-body" dangerouslySetInnerHTML={{ __html: e.html }} />
              </div>
            ))}
          </div>
        ))}

        <div className="callout">
          <div className="co-icon"><Icon name="spark" size={16} /></div>
          <div>
            <div className="co-k">Authoring suggestion</div>
            <div className="co-body">{log.suggestion}</div>
          </div>
        </div>
      </div>
    </div>
  );
}

Object.assign(window, { SleepLogView });

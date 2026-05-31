/* Profile view — cognitive dossier: traits, patterns, relationships */
function ProfileView({ char, profile }) {
  const Icon = window.Icon;

  if (!profile) {
    return (
      <div className="scroll">
        <div className="empty">
          <div className="e-mark"><Icon name="profile" size={22} /></div>
          <div className="e-title">No dossier yet for {char.name}</div>
          <div className="e-desc">
            The agent hasn't gathered enough evidence to model {char.name.split(" ")[0]}.
            Hold a few conversations, then run a consolidation cycle.
          </div>
        </div>
      </div>
    );
  }

  const center = profile.relationships.find((r) => r.center);

  return (
    <div className="scroll">
      <div className="page">
        <div className="page-head">
          <div className="page-title">Cognitive dossier</div>
          <div className="page-desc">
            What the agent currently believes about {char.name} — derived from {NMA_NOVEL.title},
            refined across {window.NMA_LOG.cycle} consolidation cycles.
          </div>
        </div>

        {/* Traits */}
        <div className="sec-label">Traits <span className="sec-count">· {profile.traits.length}</span></div>
        <div>
          {profile.traits.map((t, i) => (
            <div className="trait" key={i}>
              <div className="trait-top">
                <div className="trait-name">
                  {t.name}
                  {t.isNew && <span className="badge-new">New</span>}
                </div>
                <div className="trait-conf">{t.conf.toFixed(2)}</div>
              </div>
              <div className="trait-bar"><i style={{ width: (t.conf * 100) + "%" }} /></div>
              <div className="trait-evidence">{t.evidence} supporting passages</div>
            </div>
          ))}
        </div>

        {/* Relationships */}
        <div className="sec-label">Relationship network</div>
        <div className="constellation">
          <svg
            style={{ position: "absolute", inset: 0, width: "100%", height: "100%" }}
            viewBox="0 0 100 100" preserveAspectRatio="none"
          >
            {profile.relationships.filter((r) => !r.center).map((r, i) => (
              <line
                key={i}
                x1={center.x} y1={center.y} x2={r.x} y2={r.y}
                stroke="rgba(255,255,255,0.12)" strokeWidth="0.25"
              />
            ))}
          </svg>
          {profile.relationships.map((r) => (
            <div
              key={r.id}
              className={"rel-node" + (r.center ? " center" : "")}
              style={{ left: r.x + "%", top: r.y + "%" }}
            >
              <div className={"ravatar " + (r.tone || "")}>{r.monogram}</div>
              <div className="rname">{r.name}</div>
              {!r.center && <div className="rrel">{r.rel}</div>}
            </div>
          ))}
        </div>

        {/* Behavior patterns */}
        <div className="sec-label">Behaviour patterns <span className="sec-count">· {profile.patterns.length}</span></div>
        <div className="patterns">
          {profile.patterns.map((p, i) => (
            <div className="pattern" key={i}>
              <div className="pcond">{p.cond} <span className="parrow">→</span></div>
              <div className="pbody">{p.body}</div>
              <div className="pstrength">
                <span className="pbars">
                  {[0, 1, 2, 3].map((b) => (
                    <i key={b} className={b < p.strength ? "on" : ""} />
                  ))}
                </span>
                <span className="ptext">{["weak", "weak", "moderate", "strong", "strong"][p.strength]}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

Object.assign(window, { ProfileView });

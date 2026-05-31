/* Conversation view — the core interaction. Controlled by App. */

function RiskBadge({ risk }) {
  return (
    <span className={"risk " + risk.level}>
      <span className="rd" />
      <span className="rlabel">{risk.label}</span>
      <span className="rpct">{risk.pct}%</span>
    </span>
  );
}

function OptionCard({ opt, i, chosen, anyChosen, onChoose }) {
  const Icon = window.Icon;
  const isChosen = chosen === i;
  const cls = "opt" + (isChosen ? " chosen" : "") + (anyChosen && !isChosen ? " dimmed" : "");
  return (
    <div className={cls} onClick={() => onChoose(i)}>
      <div className="opt-check"><Icon name="check" size={13} stroke={2.4} /></div>
      <div className="opt-head">
        <span className="opt-idx">{opt.idx}</span>
        <RiskBadge risk={opt.risk} />
      </div>
      <div className="opt-title">{opt.title}</div>
      <div className="opt-voice">{opt.voice}</div>
      <div className="opt-foot">
        <span className={"tagchip" + (opt.tagNew ? " new" : "")}>
          {opt.tagNew && <Icon name="spark" size={11} />}
          {opt.tag}
        </span>
      </div>
    </div>
  );
}

function FeedbackBar({ feedback, note, submitted, onFeedback, onNote, onSubmit }) {
  const Icon = window.Icon;
  if (submitted) {
    return (
      <div className="feedback fadein">
        <div className="fb-done">
          <Icon name="check" size={14} stroke={2.4} />
          Logged to memory · will consolidate during tonight's cycle
        </div>
      </div>
    );
  }
  const opts = [
    { v: "fits", label: "Fits Victor", level: "low" },
    { v: "drift", label: "A little off", level: "med" },
    { v: "off", label: "Not him", level: "high" },
  ];
  return (
    <div className="feedback fadein">
      <div className="fb-q">
        <Icon name="profile" size={14} />
        How true does this feel to the character you know?
      </div>
      <div className="fb-opts">
        {opts.map((o) => (
          <button
            key={o.v}
            className={"fb-btn" + (feedback === o.v ? " sel" : "")}
            onClick={() => onFeedback(o.v)}
          >
            {o.label}
          </button>
        ))}
      </div>
      <div className="fb-note">
        <textarea
          placeholder="Optional — note why, in your own words. This becomes a memory."
          value={note}
          onChange={(e) => onNote(e.target.value)}
        />
      </div>
      <div className="row-actions">
        <button className="btn primary" disabled={!feedback} onClick={onSubmit}>
          <Icon name="check" size={14} /> Save to memory
        </button>
      </div>
    </div>
  );
}

function ConversationView({ char, scene, options, convo, actions, hasContent }) {
  const Icon = window.Icon;
  const scrollRef = React.useRef(null);

  React.useEffect(() => {
    const el = scrollRef.current;
    if (el && convo.turns && convo.turns.length) {
      el.scrollTop = el.scrollHeight;
    }
  }, [convo.turns, convo.thinking]);

  if (!hasContent) {
    return (
      <div className="scroll" ref={scrollRef}>
        <div className="empty">
          <div className="e-mark"><Icon name="chat" size={22} /></div>
          <div className="e-title">{char.name} is still taking shape</div>
          <div className="e-desc">
            Confidence is {char.confidence.toFixed(2)}. Ask {char.name.split(" ")[0]} a question
            to begin building their model — every answer and your feedback feeds the next
            consolidation cycle.
          </div>
        </div>
        <Composer char={char} onSend={actions.onSend} />
      </div>
    );
  }

  const anyChosen = convo.chosen !== null && convo.chosen !== undefined;

  return (
    <div className="scroll" ref={scrollRef}>
      <div className="convo">
        <div className="scene-card">
          <div className="scene-eyebrow">{scene.eyebrow}</div>
          <div className="scene-text">{scene.text}</div>
          <span className="scene-q">{scene.question}</span>
        </div>

        <div className="turn-label">
          <Icon name="spark" size={12} /> {options.length} development directions, ranked by fit
        </div>

        <div className="options">
          {options.map((opt, i) => (
            <OptionCard
              key={i}
              opt={opt}
              i={i}
              chosen={convo.chosen}
              anyChosen={anyChosen}
              onChoose={actions.onChoose}
            />
          ))}
        </div>

        {anyChosen && (
          <FeedbackBar
            feedback={convo.feedback}
            note={convo.note}
            submitted={convo.submitted}
            onFeedback={actions.onFeedback}
            onNote={actions.onNote}
            onSubmit={actions.onSubmit}
          />
        )}

        {/* follow-up turns */}
        {convo.turns.map((t, ti) => (
          <div key={ti}>
            <div className="user-turn fadein">
              <div className="user-bubble">{t.text}</div>
            </div>
            {t.options && (
              <React.Fragment>
                <div className="turn-label">
                  <Icon name="spark" size={12} /> {t.options.length} directions
                </div>
                <div className="options">
                  {t.options.map((opt, i) => (
                    <OptionCard key={i} opt={opt} i={i} chosen={null} anyChosen={false} onChoose={() => {}} />
                  ))}
                </div>
              </React.Fragment>
            )}
          </div>
        ))}

        {convo.thinking && (
          <div className="thinking fadein">
            <span className="pulse"><i /><i /><i /></span>
            Recalling {char.name.split(" ")[0]}'s patterns…
          </div>
        )}
      </div>

      <Composer char={char} onSend={actions.onSend} />
    </div>
  );
}

function Composer({ char, onSend }) {
  const Icon = window.Icon;
  const [val, setVal] = React.useState("");
  const submit = () => {
    const v = val.trim();
    if (!v) return;
    onSend(v);
    setVal("");
  };
  return (
    <div className="composer-wrap">
      <div className="composer">
        <div className="composer-inner">
          <textarea
            rows={1}
            placeholder={"Pose a scenario, or ask what " + char.name.split(" ")[0] + " would do…"}
            value={val}
            onChange={(e) => setVal(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); submit(); }
            }}
          />
          <button className="send-btn" disabled={!val.trim()} onClick={submit}>
            <Icon name="send" size={17} stroke={1.9} />
          </button>
        </div>
      </div>
    </div>
  );
}

Object.assign(window, { ConversationView, Composer, OptionCard, RiskBadge });

/* Narrative Memory Agent — app shell, routing, state, tweaks */
const { useState, useEffect, useCallback } = React;

const TWEAK_DEFAULTS = /*EDITMODE-BEGIN*/{
  "accent": "#ededf2",
  "density": "comfortable",
  "voice": "on"
}/*EDITMODE-END*/;

const ACCENT_KEYS = { "#ededf2": "mono", "#b18cf0": "iris", "#7c8cff": "blue", "#5db8a4": "teal" };

function freshConvo(seed) {
  return { chosen: null, feedback: null, note: "", submitted: false, turns: [], thinking: false, ...seed };
}

function App() {
  const {
    Sidebar, ConversationView, ProfileView, SleepLogView, SettingsView, Icon,
    TweaksPanel, TweakSection, TweakColor, TweakRadio, useTweaks,
    NMA_CHARACTERS, NMA_NOVEL, NMA_SCENE, NMA_OPTIONS, NMA_FOLLOWUP, NMA_PROFILE, NMA_LOG,
  } = window;

  const [t, setTweak] = useTweaks(TWEAK_DEFAULTS);
  const [activeChar, setActiveChar] = useState("victor");
  const [view, setView] = useState("conversation");
  const [convoMap, setConvoMap] = useState(() => ({ victor: freshConvo() }));

  // apply tweaks to <html>
  useEffect(() => {
    const r = document.documentElement;
    r.setAttribute("data-accent", ACCENT_KEYS[t.accent] || "mono");
    r.setAttribute("data-density", t.density);
    r.setAttribute("data-voice", t.voice);
  }, [t.accent, t.density, t.voice]);

  const char = NMA_CHARACTERS.find((c) => c.id === activeChar);
  const hasContent = activeChar === "victor";
  const convo = convoMap[activeChar] || freshConvo();

  const updateConvo = useCallback((fn) => {
    setConvoMap((m) => ({ ...m, [activeChar]: fn(m[activeChar] || freshConvo()) }));
  }, [activeChar]);

  const actions = {
    onChoose: (i) => updateConvo((c) => (c.submitted ? c : { ...c, chosen: i, feedback: null })),
    onFeedback: (v) => updateConvo((c) => ({ ...c, feedback: v })),
    onNote: (text) => updateConvo((c) => ({ ...c, note: text })),
    onSubmit: () => updateConvo((c) => ({ ...c, submitted: true })),
    onSend: (text) => {
      updateConvo((c) => ({ ...c, thinking: true }));
      const who = activeChar;
      setTimeout(() => {
        setConvoMap((m) => {
          const c = m[who] || freshConvo();
          return {
            ...m,
            [who]: {
              ...c,
              thinking: false,
              turns: [...c.turns, { text, options: NMA_FOLLOWUP.options }],
            },
          };
        });
      }, 1100);
    },
  };

  const onSelectChar = (id) => {
    setActiveChar(id);
    if (view === "settings") setView("conversation");
    if (!convoMap[id]) setConvoMap((m) => ({ ...m, [id]: freshConvo() }));
  };

  const tabs = [
    { id: "conversation", label: "Conversation", icon: "chat" },
    { id: "profile", label: "Profile", icon: "profile" },
    { id: "sleep", label: "Sleep log", icon: "moon" },
  ];

  return (
    <div className="app">
      <Sidebar
        characters={NMA_CHARACTERS}
        activeChar={activeChar}
        onSelectChar={onSelectChar}
        view={view}
        onNav={setView}
        novel={NMA_NOVEL}
      />

      <div className="main">
        {view === "settings" ? (
          <div className="topbar">
            <div className="tb-id">
              <div className="tb-avatar"><Icon name="settings" size={17} /></div>
              <div>
                <div className="tb-title">Source &amp; settings</div>
                <div className="tb-sub">{NMA_NOVEL.title} · {NMA_CHARACTERS.length} characters</div>
              </div>
            </div>
          </div>
        ) : (
          <div className="topbar">
            <div className="tb-id">
              <div className="tb-avatar">{char.monogram}</div>
              <div>
                <div className="tb-title">{char.name}</div>
                <div className="tb-sub">{NMA_NOVEL.title} · {NMA_NOVEL.author}</div>
              </div>
            </div>

            <div className="tabs">
              {tabs.map((tb) => (
                <button
                  key={tb.id}
                  className={"tab" + (view === tb.id ? " active" : "")}
                  onClick={() => setView(tb.id)}
                >
                  <Icon name={tb.icon} size={14} /> {tb.label}
                </button>
              ))}
            </div>

            <div className="confbox" style={{ marginLeft: 16 }}>
              <span className="cf-label">Conf</span>
              <span className="confbar"><i style={{ width: (char.confidence * 100) + "%" }} /></span>
              <span className="cf-val">{char.confidence.toFixed(2)}</span>
            </div>
          </div>
        )}

        {view === "conversation" && (
          <ConversationView
            char={char}
            scene={NMA_SCENE}
            options={NMA_OPTIONS}
            convo={convo}
            actions={actions}
            hasContent={hasContent}
          />
        )}
        {view === "profile" && <ProfileView char={char} profile={NMA_PROFILE[activeChar]} />}
        {view === "sleep" && <SleepLogView char={char} log={NMA_LOG} />}
        {view === "settings" && <SettingsView novel={NMA_NOVEL} />}
      </div>

      <TweaksPanel>
        <TweakSection label="Appearance" />
        <TweakColor
          label="Accent"
          value={t.accent}
          options={["#ededf2", "#b18cf0", "#7c8cff", "#5db8a4"]}
          onChange={(v) => setTweak("accent", v)}
        />
        <TweakRadio
          label="Density"
          value={t.density}
          options={["comfortable", "compact"]}
          onChange={(v) => setTweak("density", v)}
        />
        <TweakSection label="Option cards" />
        <TweakRadio
          label="Character voice"
          value={t.voice}
          options={["on", "off"]}
          onChange={(v) => setTweak("voice", v)}
        />
      </TweaksPanel>
    </div>
  );
}

ReactDOM.createRoot(document.getElementById("root")).render(<App />);

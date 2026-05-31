"use client";

import { useState, useCallback } from "react";
import Sidebar from "@/components/Sidebar";
import ConversationView from "@/components/ConversationView";
import ProfileView from "@/components/ProfileView";
import SleepLogView from "@/components/SleepLogView";
import SettingsView from "@/components/SettingsView";
import {
  NMA_CHARACTERS,
  NMA_NOVEL,
  NMA_SCENE,
  NMA_OPTIONS,
  NMA_FOLLOWUP,
  NMA_PROFILE,
  NMA_LOG,
  freshConvo,
} from "@/lib/data";

export default function Home() {
  const [activeChar, setActiveChar] = useState("victor");
  const [view, setView] = useState("conversation");
  const [convoMap, setConvoMap] = useState<Record<string, ReturnType<typeof freshConvo>>>(
    () => ({ victor: freshConvo() })
  );

  const char = NMA_CHARACTERS.find((c) => c.id === activeChar)!;
  const convo = convoMap[activeChar] ?? freshConvo();
  const profile = NMA_PROFILE[activeChar];
  const hasContent = activeChar === "victor"; // Victor has scene data

  const updateConvo = useCallback(
    (patch: Partial<ReturnType<typeof freshConvo>>) => {
      setConvoMap((prev) => ({
        ...prev,
        [activeChar]: { ...prev[activeChar] ?? freshConvo(), ...patch },
      }));
    },
    [activeChar]
  );

  const actions = {
    onChoose: (i: number) => updateConvo({ chosen: i }),
    onFeedback: (v: string) => updateConvo({ feedback: v }),
    onNote: (v: string) => updateConvo({ note: v }),
    onSubmit: () => updateConvo({ submitted: true }),
    onSend: (text: string) => {
      const prev = convoMap[activeChar] ?? freshConvo();
      updateConvo({
        thinking: true,
        turns: [...prev.turns, { text, options: NMA_FOLLOWUP.options }],
      });
      setTimeout(() => updateConvo({ thinking: false }), 1500);
    },
  };

  return (
    <div className="app-shell">
      <Sidebar
        characters={NMA_CHARACTERS}
        activeChar={activeChar}
        novel={NMA_NOVEL}
        view={view}
        onSelectChar={(id) => {
          setActiveChar(id);
          setView("conversation");
        }}
        onNav={setView}
      />

      <main className="main-content">
        {/* Nav tabs */}
        <div style={{
          display: "flex", gap: 4, padding: "0 40px", paddingTop: 20,
          borderBottom: "1px solid var(--line)",
        }}>
          {[
            { id: "conversation", label: "💬 对话" },
            { id: "profile", label: "🧠 档案" },
            { id: "sleeplog", label: "💤 巩固日志" },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setView(tab.id)}
              style={{
                background: view === tab.id ? "var(--accent-soft)" : "none",
                border: "none",
                borderBottom: view === tab.id ? "2px solid var(--accent)" : "2px solid transparent",
                color: view === tab.id ? "var(--ink)" : "var(--ink-3)",
                padding: "8px 16px",
                fontSize: 13,
                fontWeight: view === tab.id ? 600 : 400,
                cursor: "pointer",
                fontFamily: "inherit",
                transition: "all 0.15s",
              }}
            >
              {tab.label}
            </button>
          ))}
        </div>

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
        {view === "profile" && (
          <ProfileView char={char} profile={profile} />
        )}
        {view === "sleeplog" && (
          <SleepLogView char={char} log={NMA_LOG} />
        )}
        {view === "settings" && (
          <SettingsView novel={NMA_NOVEL} />
        )}
      </main>
    </div>
  );
}

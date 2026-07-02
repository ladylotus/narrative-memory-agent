"use client";

import { useState, useCallback, useEffect } from "react";
import Sidebar from "@/components/Sidebar";
import ConversationView from "@/components/ConversationView";
import ProfileView from "@/components/ProfileView";
import SleepLogView from "@/components/SleepLogView";
import SettingsView from "@/components/SettingsView";
import IngestionView from "@/components/IngestionView";
import ErrorToast from "@/components/ErrorToast";
import type { ErrorInfo } from "@/components/ErrorToast";
import {
  fetchCharacters,
  askCharacter,
  fetchProfile,
  triggerSleep,
  submitFeedback,
  fetchResumeStatus,
  checkpointSession,
  clearSession,
  deleteCharacter,
} from "@/lib/api";
import { NMA_NOVEL, freshConvo } from "@/lib/data";
import type { Character, Option, ConvoState, Scene } from "@/lib/types";
import type { SleepReport } from "@/lib/sleep-types";

export default function Home() {
  const [characters, setCharacters] = useState<Character[]>([]);
  const [activeChar, setActiveChar] = useState<string>("");
  const [view, setView] = useState("conversation");
  const [convoMap, setConvoMap] = useState<Record<string, ConvoState>>({});
  const [scene, setScene] = useState<Scene | null>(null);
  const [options, setOptions] = useState<Option[]>([]);
  const [profile, setProfile] = useState<any>(null);
  const [sleepReport, setSleepReport] = useState<SleepReport | null>(null);
  const [isSleeping, setIsSleeping] = useState(false);
  const [feedbackPreference, setFeedbackPreference] = useState<"always" | "on-ooc" | "never">("always");
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState<ErrorInfo | null>(null);
  const [resumeStatus, setResumeStatus] = useState<{ has_resumed: boolean; turn_count: number; last_question: string } | null>(null);

  // Load character list on mount
  useEffect(() => {
    fetchCharacters().then((chars) => {
      setCharacters(chars);
      if (chars.length > 0) {
        setActiveChar(chars[0].id);
      }
      setLoading(false);
    }).catch(() => {
      setLoading(false);
      setErrorMsg({ type: "backend-down" });
    });
  }, []);

  // When active character changes, load profile + build initial scene
  useEffect(() => {
    if (!activeChar) return;
    const char = characters.find((c) => c.id === activeChar);
    if (!char) return;

    fetchProfile(activeChar).then((p) => {
      setProfile(p);
      if (!p) {
        setErrorMsg({ type: "character-not-found", character: activeChar });
        return;
      }
      // Build an initial scene from the character's backstory
      if (p) {
        setScene({
          eyebrow: `📖 ${char.name} · Current Status`,
          text: `${char.name} stands before you.${
            p.arc_stage
              ? ` Arc stage: ${p.arc_stage}.`
              : ""
          }`,
          question: `What would you ask ${char.name.split(" ")[0]}?`,
        });
      }
    });
    // Check for cross-session memory (returning user)
    fetchResumeStatus(activeChar).then((r) => {
      if (r.has_resumed) {
        setResumeStatus({ has_resumed: true, turn_count: r.turn_count, last_question: r.last_question });
        // Restore conversation history into convoMap
        if (r.conversation_history && r.conversation_history.length > 0) {
          const restoredTurns = r.conversation_history.map((entry: any) => {
            const options = (entry.options || []).map((opt: any, i: number) => {
              const level = opt.level || "low";
              const labels: Record<string, string> = {
                low: "✅ Fitting",
                med: "⚠️ Off-track",
                high: "❌ OOC",
              };
              let label = labels[level] || "✅ Fitting";
              const oocType = opt.type || "normal";
              if (oocType === "violation") label = "🚫 OOC Violation";
              else if (oocType === "surprise") label = "🟠 Surprising";
              const scores: Record<string, number> = {};
              for (const k of ["T", "B", "D", "C", "P"]) {
                scores[k] = typeof opt[k] === "number" ? opt[k] : 0.5;
              }
              return {
                idx: `Direction ${String(i + 1).padStart(2, "0")}`,
                title: opt.description || "",
                voice: opt.voice || "",
                tag: opt.tag || label,
                tagNew: false,
                risk: { level, label, pct: opt.pct || 0, type: oocType },
                oocScores: scores,
              };
            });
            return {
              text: entry.text || "",
              options,
              chosen: entry.chosen,
            };
          });
          setConvoMap((prev) => ({
            ...prev,
            [activeChar]: { ...(prev[activeChar] ?? freshConvo()), turns: restoredTurns },
          }));
        }
      } else {
        setResumeStatus(null);
      }
    });
    // Reset conversation state
    setOptions([]);
    setSleepReport(null);
  }, [activeChar, characters]);

  const activeCharacter = characters.find((c) => c.id === activeChar);
  const convo = convoMap[activeChar] ?? freshConvo();

  const updateConvo = useCallback(
    (patch: Partial<ConvoState>) => {
      setConvoMap((prev) => ({
        ...prev,
        [activeChar]: { ...(prev[activeChar] ?? freshConvo()), ...patch },
      }));
    },
    [activeChar]
  );

  const handleSend = useCallback(
    async (text: string) => {
      if (!activeChar) return;
      updateConvo({ thinking: true });

      // Build context from scene + user question
      const fullQuestion = scene
        ? `${scene.text}\n\n${text}`
        : text;

      try {
        const result = await askCharacter(activeChar, fullQuestion, 4);
        setScene((prev) =>
          prev
            ? { ...prev, text: fullQuestion, question: "What do you do?" }
            : prev
        );
        setOptions(result.options);

        const prev = convoMap[activeChar] ?? freshConvo();
        updateConvo({
          thinking: false,
          chosen: null,
          submitted: false,
          turns: [
            ...prev.turns,
            { text, options: [], chosen: null },
          ],
        });
      } catch (e) {
        updateConvo({ thinking: false });
        setErrorMsg({
          type: "generation-failed",
          detail: e instanceof Error ? e.message : "Server unreachable",
        });
      }
    },
    [activeChar, scene, convoMap, updateConvo]
  );

  const actions = {
    onChoose: (i: number) => updateConvo({ chosen: i }),
    onToggleMark: (v: string) => {
      const current = convo.marks;
      const next = current.includes(v)
        ? current.filter((m) => m !== v)
        : [...current, v];
      updateConvo({ marks: next });
    },
    onNote: (v: string) => updateConvo({ note: v }),
    onSubmit: async () => {
      if (!activeChar || convo.chosen === null || convo.chosen === undefined) return;
      const chosenOpt = options[convo.chosen];
      if (!chosenOpt) return;

      await submitFeedback(
        activeChar,
        chosenOpt.idx,
        chosenOpt.oocScores,
        convo.marks,
      );

      // Save this round's options + choice into conversation history
      const prev = convoMap[activeChar] ?? freshConvo();
      const updatedTurns = [...prev.turns];
      if (updatedTurns.length > 0) {
        const lastIdx = updatedTurns.length - 1;
        updatedTurns[lastIdx] = {
          ...updatedTurns[lastIdx],
          options: options,
          chosen: convo.chosen,
        };
      }
      updateConvo({ submitted: true, turns: updatedTurns });
    },
    onSend: handleSend,
  };

  const handleSelectChar = useCallback((id: string) => {
    setActiveChar(id);
    setView("conversation");
  }, []);

  const handleRunSleep = useCallback(async () => {
    if (!activeChar) return;
    setIsSleeping(true);
    setSleepReport(null);
    const report = await triggerSleep(activeChar);
    setIsSleeping(false);
    if (report) {
      setSleepReport(report);
      setView("sleeplog");
    } else {
      setErrorMsg({ type: "sleep-failed" });
    }
  }, [activeChar]);

  const handleRefreshCharacters = useCallback(() => {
    fetchCharacters().then(setCharacters).catch(() => {
      setErrorMsg({ type: "backend-down" });
    });
  }, []);

  const handleDeleteCharacter = useCallback(async (name: string) => {
    if (!confirm(`Delete "${name}" and all associated data? This cannot be undone.`)) return;
    try {
      await deleteCharacter(name);
      // Remove from local state
      const remaining = characters.filter((c) => c.id !== name);
      setCharacters(remaining);
      // Switch to the first remaining character if we deleted the active one
      if (activeChar === name && remaining.length > 0) {
        setActiveChar(remaining[0].id);
        setView("conversation");
      } else if (remaining.length === 0) {
        setActiveChar("");
      }
      setErrorMsg(null);
    } catch (e) {
      setErrorMsg({
        type: "generic",
        detail: e instanceof Error ? e.message : "Failed to delete character",
      });
    }
  }, [characters, activeChar]);

  if (loading) {
    return (
      <div className="app-shell">
        <div className="main-content" style={{ display: "flex", alignItems: "center", justifyContent: "center" }}>
          <div className="thinking-anim fadein">
            <div className="thinking-anim-icon">
              <span className="ta-quill">&#x2727;</span>
            </div>
            <div className="thinking-anim-text">
              Unfolding the story…
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!activeCharacter) {
    return (
      <div className="app-shell">
        <div className="main-content" style={{ display: "flex", alignItems: "center", justifyContent: "center" }}>
          <div className="empty">
            <div className="e-mark">📖</div>
            <div className="e-title">No characters</div>
            <div className="e-desc">No novel has been ingested yet. Import some text to get started.</div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="app-shell">
      <Sidebar
        characters={characters}
        activeChar={activeChar}
        novel={NMA_NOVEL}
        view={view}
        onSelectChar={handleSelectChar}
        onNav={setView}
      />

      <main className="main-content">
        <ErrorToast error={errorMsg} onDismiss={() => setErrorMsg(null)} />
        {/* Nav tabs */}
        <div style={{
          display: "flex", gap: 4, padding: "0 40px", paddingTop: 20,
          borderBottom: "1px solid var(--line)",
        }}>
          {[
            { id: "conversation", label: "💬 Chat" },
            { id: "profile", label: "🧠 Profile" },
            { id: "sleeplog", label: "💤 Sleep Log" },
            { id: "ingestion", label: "📖 Novel" },
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
            char={activeCharacter}
            scene={scene ?? { eyebrow: "", text: "", question: `What would you ask ${activeCharacter.name.split(" ")[0]}?` }}
            options={options}
            convo={convo}
            actions={actions}
            hasContent={!!scene}
            feedbackPreference={feedbackPreference}
            resumeStatus={resumeStatus}
          />
        )}
        {view === "profile" && (
          <ProfileView char={activeCharacter} profile={profile ?? undefined} onDelete={handleDeleteCharacter} />
        )}
        {view === "sleeplog" && (
          <SleepLogView
            char={activeCharacter}
            report={sleepReport}
            isSleeping={isSleeping}
            onRunSleep={handleRunSleep}
          />
        )}
        {view === "ingestion" && (
          <IngestionView onCharactersCreated={handleRefreshCharacters} />
        )}
        {view === "settings" && (
          <SettingsView
            novel={NMA_NOVEL}
            feedbackPreference={feedbackPreference}
            onChangeFeedbackPreference={setFeedbackPreference}
            onNavigate={setView}
          />
        )}
      </main>
    </div>
  );
}

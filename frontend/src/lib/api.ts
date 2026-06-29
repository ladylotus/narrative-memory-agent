/**
 * API adapter — connects the frontend to the FastAPI backend.
 *
 * All type conversions happen here so components stay clean.
 */

import type { Character, Option, CharacterProfile as FrontendProfile, Trait, BehaviorPattern, Relationship } from "./types";

const API =
  (typeof process !== "undefined" &&
    (process.env as Record<string, string>)["NEXT_PUBLIC_API_URL"]) ||
  "http://localhost:8000";

// ── Backend raw types ──────────────────────────────────

interface BOption {
  description: string;
  ooc_risk: number;
  ooc_details: Record<string, number | string>; // text, level, tag, type, T/B/D/C/P
}

interface BAskResp {
  status: string;
  character: string;
  question: string;
  options: BOption[];
}

interface BProfileResp {
  status: string;
  character: string;
  aliases: string[];
  traits: {
    name: string;
    category: string;
    description: string;
    confidence: number;
  }[];
  relations: Record<string, string>;
  motivation: string;
  arc_stage: string;
  backstory: string;
}

interface BSleepResp {
  status: string;
  character: string;
  message: string;
  report: {
    phase1: {
      events_analyzed: number;
      conflicts_detected: { intent: string; conflicting_keywords: string[]; event: string; severity: string }[];
      importance_adjustments: { event: string; from: number; to: number; reason: string }[];
    };
    phase2: {
      patterns_extracted: string[];
      events_pruned: number;
      trait_updates: { trait: string; action: string; from: number; to: number }[];
      arc_stage_change: { from: string; to: string; reason: string } | null;
    };
    phase3: {
      summary: string;
      confidence_delta: number;
    };
  };
}

/**
 * Fetch resume status — check if a character has saved session state
 */
export interface ResumeStatus {
  character: string;
  has_resumed: boolean;
  turn_count: number;
  last_question: string;
  preferred_profile: number[] | null;
}

export async function fetchResumeStatus(character: string): Promise<ResumeStatus> {
  const res = await fetch(`${API}/session/resume/${encodeURIComponent(character)}`);
  if (!res.ok) return { character, has_resumed: false, turn_count: 0, last_question: "", preferred_profile: null };
  return res.json();
}

/**
 * Checkpoint working memory — save current session state
 */
export async function checkpointSession(character: string, lastQuestion?: string): Promise<void> {
  await fetch(`${API}/session/checkpoint`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ character, last_question: lastQuestion ?? "" }),
  });
}

/**
 * Clear session state — after sleep consolidation
 */
export async function clearSession(character: string): Promise<void> {
  await fetch(`${API}/session/clear`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ character }),
  });
}

// ── Character metadata (static until IngestionService) ─

const CHARACTER_META: Record<string, { emoji: string; role: string }> = {
  "Caelan Ashmark": { emoji: "🐺", role: "Protagonist · Alpha" },
  "Elizabeth Bennet": { emoji: "📖", role: "Protagonist · Pride & Prejudice" },
  "Fitzwilliam Darcy": { emoji: "🎩", role: "Love Interest · Pride & Prejudice" },
  "Beta Theron": { emoji: "👤", role: "Character" },
  "Lena": { emoji: "👤", role: "Character" },
  "Maren": { emoji: "👤", role: "Character" },
  "Nell": { emoji: "👤", role: "Character" },
};

// ── Public API ─────────────────────────────────────────

export interface IngestResult {
  status: string;
  title: string;
  chunks_processed: number;
  events_extracted: number;
  characters_found: string[];
  new_characters: string[];
}

/** Ingest novel text — extract events + characters into memory layers. */
export async function ingestNovel(
  text: string,
  title?: string,
): Promise<IngestResult> {
  const res = await fetch(`${API}/ingest/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text, title }),
  });
  if (!res.ok) {
    const err = await res.text();
    throw new Error(err || `HTTP ${res.status}`);
  }
  return res.json();
}

/** Fetch the list of characters from the backend. */
export async function fetchCharacters(): Promise<Character[]> {
  const res = await fetch(`${API}/profile/`);
  const json = await res.json();
  const names: string[] = json.characters ?? [];
  return names.map((name) => {
    const meta = CHARACTER_META[name];
    return {
      id: name,
      name,
      emoji: meta?.emoji ?? "📄",
      role: meta?.role ?? "Character",
      confidence: 0.5,
      status: "consolidated" as const,
    };
  });
}

/** Ask the character a question. Returns frontend-ready options. */
export async function askCharacter(
  character: string,
  question: string,
  numOptions = 3,
): Promise<{ question: string; options: Option[] }> {
  const res = await fetch(`${API}/ask/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ character, question, num_options: numOptions }),
  });
  const data: BAskResp = await res.json();
  return {
    question: data.question,
    options: data.options.map(mapOption),
  };
}

/** Fetch a character's profile from the backend. */
export async function fetchProfile(name: string): Promise<FrontendProfile | null> {
  const res = await fetch(`${API}/profile/${encodeURIComponent(name)}`);
  if (!res.ok) return null;
  const data: BProfileResp = await res.json();

  return {
    traits: data.traits.map((t) => ({
      name: t.name,
      conf: t.confidence,
      evidence: 0, // backend doesn't track evidence count yet
      isNew: false,
    })),
    patterns: [], // backend doesn't have behavior patterns yet
    relationships: Object.entries(data.relations).map(([name, rel], i) => ({
      id: `rel_${i}`,
      name,
      emoji: "👤",
      rel,
      x: 20 + (i * 60) / Math.max(Object.keys(data.relations).length, 1),
      y: 30 + (i % 2) * 40,
      tone: "warm",
    })),
    // Extra fields consumed by UI (accessed via casts in components)
    arc_stage: data.arc_stage,
    motivation: data.motivation,
    backstory: data.backstory,
  };
}

/** Trigger a sleep cycle and return the report. */
export async function triggerSleep(name: string): Promise<BSleepResp["report"] | null> {
  const res = await fetch(`${API}/sleep/${encodeURIComponent(name)}`, { method: "POST" });
  if (!res.ok) return null;
  const data: BSleepResp = await res.json();
  return data.report ?? null;
}

/** Submit user feedback on a chosen option → updates Generation Bias. */
export async function submitFeedback(
  character: string,
  optionLabel: string,
  scores: Record<string, number>,
  marks: string[],
): Promise<{ updated: boolean; preferred_profile: number[] | null }> {
  const res = await fetch(`${API}/feedback/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ character, option_label: optionLabel, scores, marks }),
  });
  if (!res.ok) {
    const err = await res.text();
    console.warn("Feedback submission failed:", err);
    return { updated: false, preferred_profile: null };
  }
  return res.json();
}

// ── Internal helpers ───────────────────────────────────

function mapOption(opt: BOption, idx: number): Option {
  const pct = Math.round(opt.ooc_risk * 100);
  let level: "low" | "med" | "high";
  if (opt.ooc_risk < 0.3) level = "low";
  else if (opt.ooc_risk < 0.6) level = "med";
  else level = "high";

  // Classify high risk: violation vs surprise
  const oocType = (opt.ooc_details?.type as string) || "normal";

  // Use backend's risk tag (low/medium/high) if available
  const backendTag = opt.ooc_details?.tag as string | undefined;

  const labels: Record<string, string> = {
    low: "✅ Fitting",
    med: "⚠️ Off-track",
    high: "❌ OOC",
  };

  // Override label based on violation/surprise type (regardless of risk level)
  let label = labels[level];
  if (oocType === "violation") label = "🚫 OOC Violation";
  else if (oocType === "surprise") label = "🟠 Surprising";

  // Extract T/B/D/C/P from ooc_details
  const scores: Record<string, number> = {};
  for (const k of ["T", "B", "D", "C", "P"]) {
    const v = opt.ooc_details?.[k];
    scores[k] = typeof v === "number" ? v : 0.5;
  }

  return {
    idx: `Direction ${String(idx + 1).padStart(2, "0")}`,
    title: opt.description,               // backend sends short title as "description"
    voice: (opt.ooc_details?.text as string) || "",  // backend puts voice text in ooc_details.text
    tag: backendTag || label,
    tagNew: false,
    risk: { level, label, pct, type: oocType as "violation" | "surprise" | "normal" },
    oocScores: scores,
  };
}

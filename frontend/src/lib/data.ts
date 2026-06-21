import type {
  Character,
  Novel,
  Scene,
  Option,
  CharacterProfile,
  SleepLog,
  Turn,
} from "./types";

export const NMA_NOVEL: Novel = {
  title: "Pride and Prejudice",
  author: "Jane Austen",
  year: 1813,
  chapters: 61,
  emoji: "📖",
};

export const NMA_CHARACTERS: Character[] = [
  {
    id: "elizabeth-bennet",
    name: "Elizabeth Bennet",
    emoji: "🧠",
    role: "Protagonist · Intelligence & Prejudice",
    confidence: 0.78,
    status: "consolidated",
    flag: "⚡ 1 unresolved conflict · pride in her own judgment",
  },
  {
    id: "fitzwilliam-darcy",
    name: "Fitzwilliam Darcy",
    emoji: "🏛️",
    role: "The Proud Suitor",
    confidence: 0.72,
    status: "consolidated",
    flag: "🔄 Arc in progress — just refused",
  },
  {
    id: "jane-bennet",
    name: "Jane Bennet",
    emoji: "🌸",
    role: "Elder Sister · Kindness Itself",
    confidence: 0.54,
    status: "forming",
  },
  {
    id: "charles-bingley",
    name: "Charles Bingley",
    emoji: "🎭",
    role: "Warm-hearted Gentleman",
    confidence: 0.49,
    status: "forming",
  },
  {
    id: "george-wickham",
    name: "George Wickham",
    emoji: "🎖️",
    role: "Charming Officer",
    confidence: 0.45,
    status: "forming",
  },
];

/* ── Demo Scene: Darcy's First Proposal (Hunsford) ── */

export const NMA_SCENE: Scene = {
  eyebrow: "📖 Hunsford Parsonage · Chapter 34",
  text: "Mr. Darcy has just arrived at the parsonage, visibly agitated. After a strained silence, he declares his admiration for you — despite your family's inferiority, despite your 'intolerable' connections. He asks for your hand.\n\nHe seems to expect gratitude. Instead, you feel a rising fury — at his arrogance, and at everything you believe he has done: separating Jane from Bingley, cheating Wickham of his inheritance.",
  question: "What do you say to Mr. Darcy?",
};

export const NMA_OPTIONS: Option[] = [
  {
    idx: "Direction 01",
    title: "Refuse him — call out his pride and his cruelty to Jane and Wickham",
    voice: '"You are the last man in the world whom I could ever be prevailed upon to marry."',
    tag: "✅ Fitting · Elizabeth's righteous anger",
    tagNew: false,
    risk: { level: "low", label: "✅ Fitting", pct: 8 },
    oocScores: { T: 0.90, B: 0.85, D: 0.10, C: 0.85, P: 0.15 },
  },
  {
    idx: "Direction 02",
    title: "Refuse him gently — claim you don't know him well enough",
    voice: '"I am sensible of the honour, sir, but I cannot accept. Pray let us speak no more of it."',
    tag: "⚠️ Off-track · Elizabeth is not gentle when wronged",
    tagNew: false,
    risk: { level: "med", label: "⚠️ Off-track", pct: 42 },
    oocScores: { T: 0.45, B: 0.40, D: 0.50, C: 0.55, P: 0.50 },
  },
  {
    idx: "Direction 03",
    title: "Accept his proposal — despite how you feel about his character",
    voice: '"I… accept, Mr. Darcy. It is a most advantageous offer."',
    tag: "❌ OOC · Elizabeth would never sell herself for security",
    tagNew: false,
    risk: { level: "high", label: "❌ OOC", pct: 88 },
    oocScores: { T: 0.10, B: 0.85, D: 0.85, C: 0.15, P: 0.90 },
  },
  {
    idx: "Direction 04",
    title: "Remain silent — wait for him to explain himself further",
    voice: "(Elizabeth says nothing, holding his gaze until he looks away first.)",
    tag: "🟠 Surprising · She is never at a loss for words",
    tagNew: true,
    risk: { level: "med", label: "🟠 Surprising", pct: 55 },
    oocScores: { T: 0.35, B: 0.30, D: 0.60, C: 0.40, P: 0.55 },
  },
];

/* ── Follow-up: Reading Darcy's Letter ── */

export const NMA_FOLLOWUP: { options: Option[] } = {
  options: [
    {
      idx: "Direction 01",
      title: "Read it again — let his words sink in",
      voice: '"Could I have been so wholly deceived?"',
      tag: "✅ Fitting · Elizabeth's intellect wrestles with new evidence",
      tagNew: false,
      risk: { level: "low", label: "✅ Fitting", pct: 15 },
      oocScores: { T: 0.80, B: 0.70, D: 0.20, C: 0.75, P: 0.25 },
    },
    {
      idx: "Direction 02",
      title: "Tear up the letter — refuse to believe a word",
      voice: '"He is a proficient in the art of deception. I will not be swayed."',
      tag: "⚠️ Off-track · She is stubborn, but not dishonest with herself",
      tagNew: false,
      risk: { level: "med", label: "⚠️ Off-track", pct: 48 },
      oocScores: { T: 0.20, B: 0.75, D: 0.70, C: 0.25, P: 0.65 },
    },
    {
      idx: "Direction 03",
      title: "Immediately go to Darcy's lodgings to apologize",
      voice: '"I must find him. I owe him that much."',
      tag: "❌ OOC · Her pride would never allow such haste",
      tagNew: false,
      risk: { level: "high", label: "❌ OOC", pct: 82 },
      oocScores: { T: 0.85, B: 0.10, D: 0.25, C: 0.80, P: 0.30 },
    },
  ],
};

/* ── Elizabeth's Cognitive Profile (at Hunsford, pre-letter) ── */

export const NMA_PROFILE: Record<string, CharacterProfile> = {
  "elizabeth-bennet": {
    traits: [
      { name: "🧠 Sharp-Witted", conf: 0.88, evidence: 14, isNew: false },
      { name: "🔍 Proud of Her Judgment", conf: 0.90, evidence: 10, isNew: false },
      { name: "🏠 Loyal to Family", conf: 0.72, evidence: 5, isNew: false },
      { name: "✊ Independent", conf: 0.85, evidence: 8, isNew: false },
      { name: "🎭 Prejudiced Against Darcy", conf: 0.78, evidence: 7, isNew: true },
    ],
    patterns: [
      { cond: "When encountering Darcy", body: "Confirms her unfavourable opinion; finds evidence to support it.", strength: 4 },
      { cond: "When Wickham speaks", body: "Believes without question; enjoys being the confidante.", strength: 3 },
      { cond: "When a sister is in distress", body: "Acts decisively; suppresses her own feelings for theirs.", strength: 3 },
      { cond: "When her judgment is challenged", body: "Doubles down before reconsidering — privately.", strength: 2 },
    ],
    relationships: [
      { id: "elizabeth-bennet", name: "Elizabeth", emoji: "🧠", rel: "Self", x: 50, y: 50, center: true, tone: "" },
      { id: "jane-bennet", name: "Jane", emoji: "🌸", rel: "Sister · Confidante", x: 50, y: 14, tone: "warm" },
      { id: "fitzwilliam-darcy", name: "Darcy", emoji: "🏛️", rel: "Proud Suitor (refused)", x: 82, y: 32, tone: "fraught" },
      { id: "george-wickham", name: "Wickham", emoji: "🎖️", rel: "Charming Confidant", x: 82, y: 72, tone: "warm" },
      { id: "charles-bingley", name: "Bingley", emoji: "🎭", rel: "Jane's Suitor (separated)", x: 16, y: 34, tone: "warm" },
      { id: "mrbennet", name: "Mr. Bennet", emoji: "📚", rel: "Father", x: 18, y: 72, tone: "warm" },
    ],
  },
};

/* ── Sleep Consolidation Log ── */

export const NMA_LOG: SleepLog = {
  cycle: 6,
  ranAt: "02:47",
  duration: "38s",
  confBefore: 0.65,
  confAfter: 0.78,
  phases: [
    {
      n: 1,
      title: "💤 Fact Consolidation",
      sub: "Extract facts from recent events, detect contradictions with known traits.",
      entries: [
        { tag: "extract", text: "Darcy's proposal triggered a strong rejection — classified as consistent with Elizabeth's independence and her poor impression of his character." },
        { tag: "conflict", text: "Detection: Elizabeth's refusal cited Wickham's story — but Wickham's account conflicts with known facts about Darcy's past. This contradiction is unresolved." },
        { tag: "trait", text: "Emerged trait «🧠 Sharp-Witted» strengthened to 0.88. New surface trait «🎭 Prejudiced Against Darcy» at 0.78." },
      ],
    },
    {
      n: 2,
      title: "🧩 Abstraction & Integration",
      sub: "Extract behavior patterns, update character understanding.",
      entries: [
        { tag: "extract", text: "Identified pattern: Elizabeth forms strong first impressions and then filters all subsequent evidence to confirm them — applies to both Wickham (positive) and Darcy (negative)." },
        { tag: "prune", text: "Pruned 3 low-weight social trivialities (dance partners, dinner conversation)." },
        { tag: "extract", text: "Emotional decoupling: 'Indignation' disassociated from 'Darcy' specific trigger — now linked to 'perceived injustice' semantic node." },
      ],
    },
    {
      n: 3,
      title: "🔍 Self-Audit Report",
      sub: "Agent examines its own understanding of the character.",
      entries: [
        { tag: "trait", text: "Character confidence: 0.65 → 0.78 📈" },
        { tag: "conflict", text: "Unresolved: Prejudice against Darcy vs. Elizabeth's fundamental honesty with herself. These two traits will collide when Darcy's letter is read." },
      ],
    },
  ],
  suggestion:
    "Next scene: Darcy's letter. Force Elizabeth's 'proud of her own judgment' trait to confront contradicting evidence — this is the turning point of her arc.",
};

export function freshConvo(): {
  chosen: number | null;
  marks: string[];
  note: string;
  submitted: boolean;
  turns: Turn[];
  thinking: boolean;
} {
  return {
    chosen: null,
    marks: [],
    note: "",
    submitted: false,
    turns: [],
    thinking: false,
  };
}

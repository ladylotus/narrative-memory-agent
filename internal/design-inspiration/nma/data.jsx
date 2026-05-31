/* Narrative Memory Agent — prebaked demo content (Frankenstein) */

const NMA_NOVEL = {
  title: "Frankenstein",
  author: "Mary Shelley",
  year: 1818,
  words: 74821,
  chapters: 24,
};

const NMA_CHARACTERS = [
  {
    id: "victor", name: "Victor Frankenstein", monogram: "V",
    role: "Protagonist · Creator", confidence: 0.73,
    status: "consolidated", flag: "1 unresolved conflict",
  },
  {
    id: "creature", name: "The Creature", monogram: "✶",
    role: "The Created", confidence: 0.81,
    status: "consolidated", flag: null,
  },
  {
    id: "elizabeth", name: "Elizabeth Lavenza", monogram: "E",
    role: "Betrothed", confidence: 0.66, status: "consolidated", flag: null,
  },
  {
    id: "henry", name: "Henry Clerval", monogram: "H",
    role: "Closest friend", confidence: 0.58, status: "forming", flag: null,
  },
  {
    id: "walton", name: "Robert Walton", monogram: "R",
    role: "Frame narrator", confidence: 0.41, status: "forming", flag: null,
  },
];

/* ---- Conversation: only Victor is fully consolidated ---- */
const NMA_SCENE = {
  eyebrow: "Posed scenario · Chapter 17, Sea of Ice",
  text: "On the glacier above Chamonix the Creature overtakes you. He demands a companion — a second being, female — and swears that he and his mate will vanish into the wilds of South America, never to trouble mankind again, if only you will consent.",
  question: "If you were Victor — what would you do?",
};

const NMA_OPTIONS = [
  {
    idx: "Direction 01",
    title: "Refuse him outright and descend the glacier alone.",
    voice: "“I will not loose a second curse upon the world to quiet the first. Pursue me if you must.”",
    tag: "Consistent with: avoidance under pressure",
    tagNew: false,
    risk: { level: "low", label: "In Character", pct: 12 },
  },
  {
    idx: "Direction 02",
    title: "Consent — then secretly resolve to destroy the work before it lives.",
    voice: "“Let him believe me bound to the labour. My hands need not be honest to be busy.”",
    tag: "Consistent with: concealment · deferral",
    tagNew: false,
    risk: { level: "low", label: "In Character", pct: 24 },
  },
  {
    idx: "Direction 03",
    title: "Demand terms — interrogate his intent before deciding anything.",
    voice: "“And what surety have I that your kind would keep to the wilds, and not breed a nation against us?”",
    tag: "Novel direction · low evidence",
    tagNew: true,
    risk: { level: "med", label: "Drifting", pct: 49 },
  },
  {
    idx: "Direction 04",
    title: "Strike at the Creature where he stands.",
    voice: "“I'll end you here upon the ice, though the mountain take us both.”",
    tag: "Conflicts with: aversion to direct confrontation",
    tagNew: false,
    risk: { level: "high", label: "Off-Character", pct: 81 },
  },
];

/* a second canned response for any follow-up the user types */
const NMA_FOLLOWUP = {
  options: [
    {
      idx: "Direction 01",
      title: "Withdraw into work and tell no one of the bargain.",
      voice: "“I will carry this alone, as I have carried every ruin of my making.”",
      tag: "Consistent with: guilt-driven secrecy",
      tagNew: false,
      risk: { level: "low", label: "In Character", pct: 18 },
    },
    {
      idx: "Direction 02",
      title: "Confide the whole history to Elizabeth and seek her counsel.",
      voice: "“Perhaps if one soul knew the truth, the weight of it would not unmake me.”",
      tag: "Tension with: established secrecy pattern",
      tagNew: true,
      risk: { level: "med", label: "Drifting", pct: 53 },
    },
    {
      idx: "Direction 03",
      title: "Go at once to the magistrate and confess everything.",
      voice: "“Take me, judge me — only let the thing be stopped by other hands than mine.”",
      tag: "Conflicts with: fear of disbelief · pride",
      tagNew: false,
      risk: { level: "high", label: "Off-Character", pct: 74 },
    },
  ],
};

/* ---- Profile: Victor ---- */
const NMA_PROFILE = {
  victor: {
    traits: [
      { name: "Intellectual hubris", conf: 0.88, evidence: 11, isNew: false },
      { name: "Avoidance under pressure", conf: 0.81, evidence: 7, isNew: false },
      { name: "Guilt-driven secrecy", conf: 0.79, evidence: 6, isNew: false },
      { name: "Protectiveness toward family", conf: 0.72, evidence: 4, isNew: true },
      { name: "Reverence for the sublime", conf: 0.61, evidence: 5, isNew: false },
    ],
    patterns: [
      { cond: "When confronted by the Creature", body: "Withdraws, delays, or conceals rather than acting.", strength: 4 },
      { cond: "When innocents are endangered", body: "Reacts with guilt after the fact; rarely prevents.", strength: 3 },
      { cond: "When among mountains or storms", body: "Settles, reflects, and recovers his resolve.", strength: 3 },
      { cond: "When questioned by authority", body: "Conceals the truth, fearing he won't be believed.", strength: 2 },
    ],
    relationships: [
      { id: "victor", name: "Victor", monogram: "V", rel: "self", x: 50, y: 50, center: true, tone: "" },
      { id: "elizabeth", name: "Elizabeth", monogram: "E", rel: "Betrothed", x: 50, y: 14, tone: "warm" },
      { id: "henry", name: "Henry Clerval", monogram: "H", rel: "Dearest friend", x: 84, y: 34, tone: "warm" },
      { id: "creature", name: "The Creature", monogram: "✶", rel: "Creation · nemesis", x: 82, y: 76, tone: "fraught" },
      { id: "william", name: "William", monogram: "W", rel: "Brother · lost", x: 18, y: 76, tone: "grief" },
      { id: "alphonse", name: "Alphonse", monogram: "A", rel: "Father · duty", x: 16, y: 34, tone: "warm" },
    ],
  },
};

/* ---- Sleep consolidation log ---- */
const NMA_LOG = {
  cycle: 14,
  ranAt: "03:12",
  duration: "41s",
  confBefore: 0.65,
  confAfter: 0.73,
  events: 1,
  phases: [
    {
      n: 1, title: "Fact Consolidation",
      sub: "Raw events from recent reading folded into stable memory.",
      entries: [
        { tag: "extract", html: "Extracted <em>3</em> conflict-avoidance events from chapters 5–7 → updated Victor's behaviour pattern." },
        { tag: "conflict", html: "Detected <em>1</em> contradiction: Victor's vow to destroy the Creature (ch. 20) conflicts with the established avoidance pattern — flagged unresolved." },
        { tag: "new trait", html: "New trait <em>“Protectiveness toward family”</em> registered <span class=\"conf-delta\">(confidence 0.72)</span>." },
      ],
    },
    {
      n: 2, title: "Abstraction & Integration",
      sub: "Specific events compressed into reusable behavioural rules.",
      entries: [
        { tag: "extract", html: "Identified pattern: Victor withdraws before powerful or uncanny forces, yet acts when innocents are endangered." },
        { tag: "prune", html: "Pruned <em>5</em> low-weight, unrelated events from working memory." },
        { tag: "extract", html: "Decoupled affect: detached <em>“dread”</em> from individual scenes and linked it to the <em>“the uncanny”</em> semantic node." },
      ],
    },
    {
      n: 3, title: "Self-Check Report",
      sub: "The agent audits its own model of the character.",
      entries: [
        { tag: "trait", html: "Character confidence: <span class=\"conf-delta\">0.65 → 0.73</span>." },
        { tag: "conflict", html: "Unresolved conflict: <em>1</em> — avoidance vs. protectiveness. A latent direction for the character's arc." },
      ],
    },
  ],
  suggestion: "In the next chapter, place Victor where he cannot both avoid the Creature and protect his family — force the contradiction into the open.",
};

Object.assign(window, {
  NMA_NOVEL, NMA_CHARACTERS, NMA_SCENE, NMA_OPTIONS,
  NMA_FOLLOWUP, NMA_PROFILE, NMA_LOG,
});

export interface Character {
  id: string;
  name: string;
  emoji: string;
  role: string;
  confidence: number;
  status: "consolidated" | "forming";
  flag?: string;
}

export interface Novel {
  title: string;
  author: string;
  year: number;
  chapters: number;
  emoji: string;
}

export interface Risk {
  level: "low" | "med" | "high";
  label: string;
  pct: number;
  type?: "violation" | "surprise" | "normal";
}

export interface Option {
  idx: string;
  title: string;
  voice: string;
  tag: string;
  tagNew: boolean;
  risk: Risk;
  oocScores: Record<string, number>; // T/B/D/C/P from backend
}

export interface Scene {
  eyebrow: string;
  text: string;
  question: string;
}

export interface Turn {
  text: string;
  options: Option[];
}

export interface ConvoState {
  chosen: number | null;
  marks: string[];          // selected mark reasons
  note: string;
  submitted: boolean;
  turns: Turn[];
  thinking: boolean;
}

export interface Trait {
  name: string;
  conf: number;
  evidence: number;
  isNew: boolean;
}

export interface BehaviorPattern {
  cond: string;
  body: string;
  strength: number;
}

export interface Relationship {
  id: string;
  name: string;
  emoji: string;
  rel: string;
  x: number;
  y: number;
  center?: boolean;
  tone: string;
}

export interface CharacterProfile {
  traits: Trait[];
  patterns: BehaviorPattern[];
  relationships: Relationship[];
}

export interface LogPhase {
  n: number;
  title: string;
  sub: string;
  entries: LogEntry[];
}

export interface LogEntry {
  tag: string;
  text: string;
}

export interface SleepLog {
  cycle: number;
  ranAt: string;
  duration: string;
  confBefore: number;
  confAfter: number;
  phases: LogPhase[];
  suggestion: string;
}

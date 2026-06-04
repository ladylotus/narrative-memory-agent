/**
 * Backend sleep report type for SleepLogView.
 * Kept here so both api.ts and SleepLogView can reference it.
 */
export interface SleepReport {
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
}

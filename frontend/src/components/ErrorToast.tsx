"use client";

import { useEffect, useState } from "react";

export type ErrorType =
  | "backend-down"
  | "character-not-found"
  | "generation-failed"
  | "sleep-failed"
  | "ingestion-failed"
  | "generic";

export interface ErrorInfo {
  type: ErrorType;
  detail?: string;
  character?: string;
}

const MESSAGES: Record<ErrorType, string> = {
  "backend-down":
    "Could not reach the backend — is FastAPI running on localhost:8000?",
  "character-not-found":
    'Could not load profile for "{character}" — the backend may not have ingested this character yet',
  "generation-failed": "Generation failed. {detail}",
  "sleep-failed":
    "Sleep consolidation failed — the backend may not have memory data for this character",
  "ingestion-failed": "Ingestion failed: {detail}",
  generic: "Something went wrong. Please try again.",
};

function formatMessage(info: ErrorInfo): string {
  let msg = MESSAGES[info.type];
  msg = msg.replace("{character}", info.character ?? "unknown");
  msg = msg.replace(
    "{detail}",
    info.detail
      ? info.detail.length > 80
        ? info.detail.slice(0, 80) + "…"
        : info.detail
      : "unknown error"
  );
  return msg;
}

/**
 * Shared error toast — auto-dismisses after 5s.
 * Uses CSS variables for dark theme consistency.
 */
export default function ErrorToast({
  error,
  onDismiss,
}: {
  error: ErrorInfo | null;
  onDismiss: () => void;
}) {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    if (error) {
      setVisible(true);
      const timer = setTimeout(() => {
        setVisible(false);
        setTimeout(onDismiss, 300);
      }, 5000);
      return () => clearTimeout(timer);
    } else {
      setVisible(false);
    }
  }, [error, onDismiss]);

  if (!error) return null;

  return (
    <div
      className={`error-toast fadein${visible ? "" : " fadeout"}`}
      onClick={onDismiss}
    >
      <span className="error-toast-icon">⚠️</span>
      <span className="error-toast-msg">{formatMessage(error)}</span>
    </div>
  );
}

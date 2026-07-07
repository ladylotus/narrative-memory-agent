# NMA Frontend

Next.js 16 (TypeScript) UI for the Narrative Memory Agent.

## Stack

- **Framework:** Next.js 16.2.6 (TypeScript)
- **Build:** Standalone output for Docker
- **UI:** Custom CSS (dark theme, CSS variables)

## Quick Start

```bash
npm install
npm run dev
# Open http://localhost:3000
```

Requires the backend running on `http://localhost:8000`.

## Architecture

```
src/
├── app/                   # App Router pages
│   ├── layout.tsx
│   ├── page.tsx           # Main app shell — character selection, routing, state
│   └── globals.css
├── components/
│   ├── Sidebar            # Character list + nav
│   ├── ConversationView   # Chat UI: options, feedback, history
│   ├── ProfileView        # Character cognitive profile display
│   ├── SleepLogView       # Sleep consolidation report
│   ├── IngestionView      # Novel text import
│   ├── SettingsView       # User preferences
│   └── ErrorToast         # Unified error handling
└── lib/
    ├── api.ts             # Backend API adapter
    ├── data.ts            # Demo character data
    ├── types.ts           # Shared TypeScript types
    └── sleep-types.ts     # Sleep report types
```

## Key Concepts

- **ConversationView** renders the chat interface with option cards, risk badges (low/medium/high), character response bubbles, and a feedback bar for GenBias learning.
- **WorkingMemory** is managed on the backend — the frontend tracks turn history in a `convoMap` and submits user choices as feedback.
- **Cross-session memory** is surfaced via a resumption banner when returning to a previously-used character.

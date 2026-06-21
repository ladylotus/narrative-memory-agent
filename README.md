# Narrative Memory Agent

**An AI-powered cognitive memory system for fictional characters.**  
*Qwen Cloud Global AI Hackathon 2026 — Track 1: MemoryAgent*

---

## 📖 What is NMA?

NMA gives fictional characters **persistent memory**. It reads novel text, builds a cognitive profile for each character, and lets authors ask "what would this character do?" — generating responses in that character's authentic voice, validated against their established personality.

Unlike generic chatbots or writing assistants, NMA treats each character as a unique cognitive entity with evolving traits, behavioral patterns, a relationship network, and a remembered conversation history across sessions.

---

## ✨ Features

| Feature | What it does |
|---------|-------------|
| **Ingest & Extract** | Paste novel chapters — NMA identifies characters, events, and relationships, then builds a 3-layer memory |
| **Ask a Character** | Query any character in their authentic voice. NMA generates 2-5 distinct development paths |
| **OOC Validation** | Every response is scored on 5 factors: Trait consistency, Behavior patterns, Semantic distance, Self-consistency, and Surprise. Violations and surprises are flagged with a risk level |
| **GenBias Learning** | When you mark a response as "what they'd do", NMA learns your preference via EMA (Exponential Moving Average) and biases future generations accordingly |
| **Memory Decay** | Events naturally fade over time. Low-importance memories are automatically archived during Sleep Consolidation, keeping the active memory set relevant and compact |
| **Episodic Memory Injection** | Every question retrieves the character's relevant memories (filtered by recall strength) and injects them into the generation prompt — characters remember what happened to them |
| **Sleep Consolidation** | An offline cycle that consolidates episodic events into abstract traits, detects contradictions, prunes noise, and produces a self-audit report — inspired by human memory consolidation |
| **Cross-Session Memory** | NMA remembers previous conversations with each character across sessions. Switch characters and come back — they remember what you talked about |

---

## 🏗 Architecture

![Architecture Diagram](docs/architecture.en.html)

The system has three layers:

```
User/Browser → Next.js Frontend → FastAPI Backend → Qwen Cloud LLM
                                        │
                              ┌─────────┴──────────┐
                              │   Dual Circuit      │
                              │  A: Generation      │
                              │  B: OOC Validation  │
                              │  ↻ GenBias (EMA)    │
                              └─────────┬──────────┘
                                        │
                    ┌───────────────────┼───────────────────┐
                    │  Working Memory   │  Episodic (SQLite)│
                    │  (Session buffer) │  (Event timeline) │
                    └───────────────────┴───────────────────┘
                    ┌───────────────────────────────────────┐
                    │  Semantic Memory (Character schemas)  │
                    │  Vector Store (ChromaDB embeddings)   │
                    └───────────────────────────────────────┘
```

For a full interactive diagram, open `docs/architecture.en.html` in a browser.

---

## 🚀 Quick Start

### Prerequisites

- Docker & docker-compose (recommended), or Python 3.11+ / Node.js 20+
- A Qwen Cloud API key ([get one here](https://dashscope-intl.aliyuncs.com/))

### Docker (recommended)

```bash
# 1. Configure your API key
cp .env.example backend/.env
# Edit backend/.env → set your QWEN_API_KEY

# 2. Build and start
./start.sh

# 3. Open http://localhost:3000
```

### Manual

```bash
# Backend
cd backend
pip install -e ".[dev]"
# Set QWEN_API_KEY in environment or backend/.env
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Frontend (in another terminal)
cd frontend
npm install
npm run dev
# Open http://localhost:3000
```

---

## 🎬 Demo Flow (2-3 minutes)

1. Open the app → Elizabeth Bennet is pre-loaded
2. Ask Elizabeth about Darcy's proposal → see 4 options with OOC risk scores
3. Pick a fitting response → feedback is saved to memory
4. View Elizabeth's cognitive profile (traits, relationships, behavior patterns)
5. Run Sleep Consolidation → see how NMA abstracts events into traits

Full demo script in `docs/demo-questions.md`.

---

## 🧠 How It Works

### Memory System

| Layer | Store | What it holds |
|-------|-------|---------------|
| **Working Memory** (Layer 1) | In-memory buffer | Current conversation context (~10 turns), attention routing |
| **Episodic Memory** (Layer 2) | SQLite | Event timeline indexed by Zwaan's 5 dimensions (time/space/causality/intentionality/self) |
| **Semantic Memory** (Layer 3) | SQLite + ChromaDB | Character schemas (traits, behavior patterns, relationships, arc stage), vector embeddings for similarity search |

### Dual Circuit Engine

- **Circuit A** (GenerationService): Reads the character's profile + conversation history + GenBias preferences, then prompts Qwen to generate diverse development paths in the character's voice
- **Circuit B** (ValidationService): Scores each option on 5 OOC factors (T/B/D/C/P), computes a composite risk score, and classifies each option as fitting/off-track/OOC violation/surprise

### GenBias (Generation Bias)

When the user marks a response as fitting, NMA updates a 5-dimensional preference vector via EMA. This vector is injected as a natural-language bias prompt in subsequent generations — the system learns what kind of responses you prefer for each character.

### Sleep Cycle

Inspired by human memory consolidation (Walker & Stickgold, 2010):
1. **Phase 1 (NREM)**: Extract facts from recent events, detect contradictions
2. **Phase 2 (REM)**: Abstract behavior patterns, prune noise, update traits
3. **Phase 3 (Self-Audit)**: Generate a confidence report and suggest next narrative steps

---

## 🛠 Tech Stack

| Category | Technology | Purpose |
|----------|-----------|---------|
| **Frontend** | Next.js (TypeScript) | UI, character management, conversation interface |
| **Backend** | FastAPI (Python 3.11) | REST API, business logic, memory management |
| **LLM** | Qwen 3.6-plus | Character voice generation, OOC evaluation |
| **Embedding** | Qwen text-embedding-v3 | Semantic similarity for OOC distance scoring |
| **Vector Store** | ChromaDB | Embedding storage and similarity search |
| **Database** | SQLite | Episodic events, character schemas, session state |
| **Deployment** | Docker / docker-compose | Containerized backend + frontend |

---

## 📄 Project Structure

```
narrative-memory-agent/
├── backend/
│   ├── app/
│   │   ├── api/           # FastAPI route handlers
│   │   ├── memory/        # 3-layer memory (working/episodic/vectors)
│   │   ├── models/        # Data models (Pydantic + dataclasses)
│   ├── services/      # Core services (generation/validation/bias/decay/sleep)
│   └── tests/             # 93 unit tests
├── frontend/
│   └── src/
│       ├── app/           # Next.js pages
│       ├── components/    # UI components
│       └── lib/           # API adapter, types, demo data
├── docs/
│   ├── architecture.en.html  # Interactive architecture diagram (English)
│   ├── architecture.zh.html  # Interactive architecture diagram (Chinese)
│   └── demo-questions.md     # Demo script
├── Dockerfile.backend
├── Dockerfile.frontend
├── docker-compose.yml
├── start.sh
└── .env.example
```

---

## 📜 License

MIT — see LICENSE for details.

---

## 🏆 Hackathon Submission

Built for the Qwen Cloud Global AI Hackathon 2026 · Track 1: MemoryAgent  
*Where characters remember who they are — and who you want them to become.*

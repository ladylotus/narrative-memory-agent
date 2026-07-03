# NMA – Narrative Memory Agent

**Track:** Track 1: MemoryAgent

---

Every fictional character faces the same problem: close the window, and they forget you existed. A chatbot that resets on every reload is not a character — it's a script. NMA gives fictional characters persistent, evolving memory across sessions, so the Elizabeth Bennet you spoke to yesterday remembers what you discussed today.

## What It Does

NMA ingests novel text and builds a cognitive profile for each character — traits, behavior patterns, motivation, arc stage, and relationships. You ask a character a question, and NMA generates 2-5 distinct responses in that character's voice, each scored for how in-character it is. Pick one, and the system learns from your choice.

The system comes pre-loaded with four characters across two novels — Elizabeth Bennet and Fitzwilliam Darcy from *Pride and Prejudice*, and Lena and Caelan Ashmark from an original Caelvorn Series work — demonstrating that the same architecture works for both canonical literary figures and original creations.

## How It Works

**Dual Circuit Engine.** Circuit A (Generation) prompts Qwen 3.6-plus with the character's full profile — backstory, traits, motivation, arc stage — to produce diverse responses. Circuit B (Validation) scores each option on five OOC factors: trait consistency, behavior patterns, semantic distance (from real ChromaDB embeddings, not LLM-estimated), self-consistency, and surprise value. Options are classified as fitting, surprising, or out-of-character.

**Two Memory Layers + Schema Store.** Working Memory buffers current conversation context and persists to SQLite for cross-session recall. Episodic Memory stores a Zwaan-indexed event timeline that decays over time — low-importance memories are archived during Sleep. The Character Schema Store (SQLite `characters` table) holds traits, behavior patterns, arc stage, motivation, and relationships — written by Ingestion and Sleep, read by Circuit A for generation. A separate Vector Store (ChromaDB) provides embedding similarity search for the OOC validation D-score (semantic distance), but is not a memory layer.

**GenBias Learning Loop.** When a user marks a response as fitting, NMA updates a 5-dimensional preference vector via EMA. This bias is injected into future generations — the system learns what responses each user prefers for each character.

**Sleep Consolidation.** Inspired by human memory consolidation: NREM extracts facts, REM abstracts behavior patterns into traits, Self-Audit reports contradictions and confidence.

**Cross-Session Persistence.** Every interaction checkpoints to SQLite. Switch characters or close the browser — come back days later, and the character remembers where you left off.

## Why It Matters

For readers who have invested hundreds of pages only to watch characters act inconsistently across sequels — consistency isn't a nice-to-have, it's the foundation of an immersive world. For authors managing multi-book series or sprawling casts where every character needs to stay internally coherent. For anyone building AI characters — in games, interactive fiction, or virtual worlds — who needs them to feel like real people with real memories, not scripts that replay on every visit.

## Tech Stack

| Category | Technology |
|----------|-----------|
| **LLM** | Qwen 3.6-plus (generation + OOC evaluation) |
| **Embedding** | Qwen text-embedding-v3 |
| **Backend** | FastAPI (Python 3.11) |
| **Frontend** | Next.js 16 (TypeScript) |
| **Database** | SQLite |
| **Vector Store** | ChromaDB |
| **Deployment** | Docker / docker-compose |

## Status

Open source (MIT). Deployed on Alibaba Cloud. Pre-loaded demo data ready with `docker compose up`.

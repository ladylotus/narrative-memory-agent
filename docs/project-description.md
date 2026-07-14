# NMA – Narrative Memory Agent

**Track:** Track 1: MemoryAgent

---

There are characters you finish a book and can't stop thinking about — who feel less like something an author made up and more like someone who was already there, on the other side of a page you can't step past. You were never meant to reach them. NMA is a door built to get as close as possible.

The difference from a companion chatbot is where the character comes from. Those apps ask you to write a persona and then act it out with you; what answers is a mask you designed. NMA surfaces the person the book already wrote — memory, traits, contradictions, and history extracted from the text itself, evolving across sessions. You don't build the character. You meet them.

## What It Does

NMA ingests novel text and builds a cognitive profile for each character — traits, behavior patterns, motivation, arc stage, and relationships. You ask a character a question, and NMA generates 2-5 distinct responses in that character's voice, each scored for how in-character it is. Pick one, and the system learns from your choice.

A fresh install comes pre-loaded with Elizabeth Bennet and Fitzwilliam Darcy from *Pride and Prejudice*. Further characters are built by the ingestion pipeline from raw novel text — the demo's Lena, Mira, and Caelan Ashmark come from my own Caelvorn Series — demonstrating that the same architecture works for both canonical literary figures and original creations.

## How It Works

**Dual Circuit Engine.** Circuit A (Generation) prompts Qwen 3.6-flash with the character's full profile — backstory, traits, motivation, arc stage — to produce diverse responses. Circuit B (Validation) scores each option on five OOC factors: trait consistency, behavior patterns, semantic distance (from real ChromaDB embeddings, not LLM-estimated), self-consistency, and surprise value. Options are classified as fitting, surprising, or out-of-character.

**Two Memory Layers + Schema Store.** Working Memory buffers current conversation context and persists to SQLite for cross-session recall. Episodic Memory stores a Zwaan-indexed event timeline that decays over time — low-importance memories are archived during Sleep. The Character Schema Store (SQLite `characters` table) holds traits, behavior patterns, arc stage, motivation, and relationships — written by Ingestion and Sleep, read by Circuit A for generation. A separate Vector Store (ChromaDB) provides embedding similarity search for the OOC validation D-score (semantic distance), but is not a memory layer.

**GenBias Learning Loop.** When a user marks a response as fitting, NMA updates a 5-dimensional preference vector via EMA. This bias is injected into future generations — the system learns what responses each user prefers for each character.

**Sleep Consolidation.** Inspired by human memory consolidation: NREM extracts facts, REM abstracts behavior patterns into traits, Self-Audit reports contradictions and confidence.

**Cross-Session Persistence.** Every interaction checkpoints to SQLite. Switch characters or close the browser — come back days later, and the character remembers where you left off.

## Why It Matters

The want is real on both sides of the book. Readers finish a series and keep living with its people — replaying the fork the character didn't take, wishing they could ask why. Authors carry a cast that has to stay coherent across books, and would give anything to check what a character actually knows before writing their next line. Both are reaching for the same thing: a character who is *there* — consistent, remembering, their own — not a script that replays on every visit.

It isn't hypothetical for me. I serialize the Caelvorn Series on Dreame (Book 1 complete), and I'm the reader at 2 a.m. as often as I'm the writer. That's why the demo characters — Lena, Mira, Caelan Ashmark — are ingested live from my own manuscript: the system is tested against the exact problem it was built to solve. I don't know yet how many people share this want strongly enough to build a product on. I built NMA to find out — starting with the one person I'm certain of.

## Tech Stack

| Category | Technology |
|----------|-----------|
| **LLM** | Qwen 3.6-flash (generation + OOC evaluation) |
| **Embedding** | Qwen text-embedding-v3 |
| **Backend** | FastAPI (Python 3.11) |
| **Frontend** | Next.js 16 (TypeScript) |
| **Database** | SQLite |
| **Vector Store** | ChromaDB |
| **Deployment** | Docker / docker-compose |

## Status

Open source (MIT). Deployed on Alibaba Cloud. Pre-loaded demo data ready with `docker compose up`.

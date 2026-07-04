# NMA — Tech Stack

## Frontend
- **Framework:** Next.js 16.2.6 (TypeScript)
- **UI:** Custom CSS (dark theme, CSS variables)
- **Build:** Standalone output for Docker

## Backend
- **Framework:** FastAPI (Python 3.11)
- **Server:** Uvicorn
- **ORM / Storage:** Raw SQLite via sqlite3 stdlib
- **Vector Store:** ChromaDB (PersistentClient)
- **Decay Service:** Time-based memory decay (`decay.py`) — recall_score formula, auto-archiving

## AI / LLM
- **Generation Model:** Qwen 3.6-flash (dashscope-intl)
- **Embedding Model:** Qwen text-embedding-v3
- **Integration:** OpenAI-compatible SDK (AsyncOpenAI)

## Testing
- **Framework:** pytest (>=8.0) + pytest-asyncio
- **Coverage:** 124 unit tests (bias, decay, validation, bias_prompt, API, sleep)

## Deployment
- **Containerization:** Docker (multi-stage builds)
- **Orchestration:** docker-compose (backend + frontend + data volume)
- **One-click start:** start.sh (env check + compose up)

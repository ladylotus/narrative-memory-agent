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

## AI / LLM
- **Generation Model:** Qwen 3.6-plus (dashscope-intl)
- **Embedding Model:** Qwen text-embedding-v3
- **Integration:** OpenAI-compatible SDK (AsyncOpenAI)

## Testing
- **Framework:** pytest 9.0 + pytest-asyncio
- **Coverage:** 80 unit tests (validation, generation, bias, bias_prompt, API, sleep)

## Deployment
- **Containerization:** Docker (multi-stage builds)
- **Orchestration:** docker-compose (backend + frontend + data volume)
- **One-click start:** start.sh (env check + compose up)

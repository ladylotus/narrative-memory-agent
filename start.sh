#!/usr/bin/env bash
# —— NMA: One-click start ——
# Qwen Cloud Hackathon — Track 1: MemoryAgent
#
# Prerequisites:
#   1. Docker & docker-compose installed
#   2. QWEN_API_KEY in backend/.env (copy from .env.example)
#
# Usage:
#   ./start.sh          # Build & start in foreground
#   ./start.sh -d       # Build & start in background (detached)
#   ./start.sh --build  # Force rebuild

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "🔧 Narrative Memory Agent — Deployment"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check prerequisites
if ! command -v docker &>/dev/null; then
  echo "❌ Docker is not installed. Install it first: https://docs.docker.com/engine/install/"
  exit 1
fi

if ! docker compose version &>/dev/null; then
  echo "❌ docker compose plugin is not installed."
  exit 1
fi

# Check env file
if [ ! -f backend/.env ]; then
  echo "⚠️  No backend/.env found. Copying from .env.example…"
  cp .env.example backend/.env
  echo "   ✏️  Edit backend/.env and set your QWEN_API_KEY"
  echo ""
fi

if grep -q "your-key-here" backend/.env 2>/dev/null; then
  echo "⚠️  QWEN_API_KEY is still the placeholder. Edit backend/.env before starting."
  exit 1
fi

# Parse args
ARGS=""
for arg in "$@"; do
  case "$arg" in
    -d) ARGS="$ARGS -d" ;;
    --build) ARGS="$ARGS --build" ;;
  esac
done

echo "🚀 Starting services…"
echo "   Backend  → http://localhost:8000"
echo "   Frontend → http://localhost:3000"
echo ""

docker compose up $ARGS

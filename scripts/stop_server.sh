#!/usr/bin/env bash
# Stop the FastAPI backend server (process listening on port 8000, or uvicorn main:app).
# Usage: ./scripts/stop_server.sh   (from backend/) or  ./stop_server.sh (from backend/scripts/)

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$BACKEND_ROOT"

PORT="${PORT:-8000}"

# Prefer lsof (macOS/Linux); fallback to finding uvicorn by command line
if command -v lsof >/dev/null 2>&1; then
  PIDS=$(lsof -ti ":$PORT" 2>/dev/null || true)
elif command -v fuser >/dev/null 2>&1; then
  PIDS=$(fuser "$PORT/tcp" 2>/dev/null || true)
else
  PIDS=""
fi

if [[ -z "$PIDS" ]]; then
  # Fallback: find uvicorn process running main:app
  PIDS=$(pgrep -f "uvicorn main:app" 2>/dev/null || true)
fi

if [[ -z "$PIDS" ]]; then
  echo "No server found on port $PORT or running uvicorn main:app."
  exit 0
fi

echo "Stopping server (PIDs: $PIDS)..."
echo "$PIDS" | xargs kill 2>/dev/null || true
echo "Done."

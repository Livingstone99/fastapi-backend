#!/usr/bin/env bash
# Start the FastAPI backend server and show logs.
# Usage: ./scripts/start_server.sh   (from backend/) or  ./start_server.sh (from backend/scripts/)

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$BACKEND_ROOT"

PORT="${PORT:-8000}"
HOST="${HOST:-127.0.0.1}"

if [[ ! -d "venv" ]]; then
  echo "Error: venv not found. Create it with: python3 -m venv venv && venv/bin/pip install -r requirements.txt"
  exit 1
fi

echo "Starting server at http://${HOST}:${PORT}"
echo "Logs below (Ctrl+C to stop)."
echo "---"
exec venv/bin/python -m uvicorn main:app --host "$HOST" --port "$PORT"

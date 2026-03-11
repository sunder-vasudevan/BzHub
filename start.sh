#!/bin/bash
# BzHub — start API + web frontend together

ROOT="$(cd "$(dirname "$0")" && pwd)"
PYTHON="$ROOT/.venv/bin/python"

echo "Starting BzHub..."

# Start FastAPI backend
echo "  -> API server (port 8000)..."
"$PYTHON" "$ROOT/bizhub.py" --api &
API_PID=$!

sleep 2

# Start Next.js frontend
echo "  -> Web frontend (port 3000)..."
cd "$ROOT/bzhub_web/bzhub_web"
bun run dev &
WEB_PID=$!

echo ""
echo "BzHub is starting:"
echo "   Web  -> http://localhost:3000"
echo "   API  -> http://localhost:8000"
echo ""
echo "Press Ctrl+C to stop both servers."

trap "echo ''; echo 'Stopping...'; kill $API_PID $WEB_PID 2>/dev/null; exit 0" INT
wait

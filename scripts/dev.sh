#!/usr/bin/env bash
set -euo pipefail
# Start backend and frontend in simple tmux panes if available; fall back to two terminals.
if command -v tmux >/dev/null 2>&1; then
  tmux new-session -d -s awsrt "cd backend && uv run uvicorn api.main:app --reload --port 8000"
  tmux split-window -h "cd frontend && npm run dev"
  tmux attach-session -t awsrt
else
  echo ">> Start backend: (in terminal 1)"
  echo "cd backend && uv run uvicorn api.main:app --reload --port 8000"
  echo ">> Start frontend: (in terminal 2)"
  echo "cd frontend && npm install && npm run dev"
fi

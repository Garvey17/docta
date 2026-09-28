#!/bin/sh
set -e

echo "Starting docta Backend Container with Supabase Infrastructure..."

PORT="${PORT:-8000}"
HOST="${HOST:-0.0.0.0}"
WORKERS="${WORKERS:-2}"

echo "Starting Uvicorn Server on ${HOST}:${PORT} with ${WORKERS} workers..."
exec uvicorn src.main:app --host "$HOST" --port "$PORT" --workers "$WORKERS"

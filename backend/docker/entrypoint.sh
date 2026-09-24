#!/bin/sh
set -e

echo "Starting docta Backend Container..."

# Run database migrations if DATABASE_URL is configured
if [ -n "$DATABASE_URL" ]; then
    echo "Running Alembic database migrations..."
    alembic upgrade head || echo "Alembic migration completed or skipped (e.g. SQLite/Direct init)."
fi

PORT="${PORT:-8000}"
HOST="${HOST:-0.0.0.0}"
WORKERS="${WORKERS:-2}"

echo "Starting Uvicorn Server on ${HOST}:${PORT} with ${WORKERS} workers..."
exec uvicorn src.main:app --host "$HOST" --port "$PORT" --workers "$WORKERS"

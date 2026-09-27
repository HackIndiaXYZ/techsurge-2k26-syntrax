#!/bin/sh
set -e

# Run database migrations
alembic upgrade head

# Start uvicorn with Railway's PORT (default 8000 for local dev)
exec uvicorn main:app --host 0.0.0.0 --port "${PORT:-8000}"

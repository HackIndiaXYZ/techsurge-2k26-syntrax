# Project Structure

`frontend/` will contain Next.js UI; `backend/` will contain FastAPI modules; `database/` is reserved for schema/migration support; `infra/` holds deployment and environment material; `ai/` is for optional offline assets only; `docs/` is the implementation source of truth. The current repository intentionally has no application implementation. Do not create a new service directory unless a documented architecture decision requires it.

# 04 ENGINEERING OPERATING MODEL

## Parallel Development Readiness
To support 4 people working simultaneously during the 17-hour build:

1. **API-Contract-First Development:** Backend defines API contracts (e.g., OpenAPI schemas or markdown contracts in docs/architecture/API_CONTRACTS.md) before implementation.
2. **Mock-Driven Frontend & AI:** Frontend (Nikhil) and AI (Sanju) develop against mock data and these API contracts.
3. **Database Ownership:** Infra (Akshaya) provisions schemas/migrations for Backend.
4. **Git Workflow:** 
   - Feature branches belong to individuals (rontend/nikhil, ackend/ramraj, etc.).
   - Pull Requests to main must be reviewed and tested locally.
5. **Integration Protocol:** Integration happens on main only when tests pass and contracts are fulfilled.

## Technology Stack Baseline
- **Frontend:** Next.js, React, TypeScript, Tailwind CSS, shadcn/ui.
- **Backend:** Python, FastAPI, Pydantic, SQLAlchemy, Alembic.
- **Data:** PostgreSQL, Supabase, pgvector.
- **AI:** Claude, Gemini, OpenRouter.
- **Cloud:** Vercel, Render.

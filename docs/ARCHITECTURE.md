# ARCHITECTURE & TECHNOLOGY STACK

**FINAL ROUND 2 ARCHITECTURE: UNKNOWN UNTIL ROUND 2 PROBLEM STATEMENT IS REVEALED.**
The following is our *default* arsenal. Technologies are conditional and should only be used if the actual problem requires them. Do not stack frameworks unnecessarily.

## Frontend (Vercel)
- **Core:** Next.js (primary framework), React, TypeScript, Tailwind CSS, shadcn/ui.
- **Interaction/Visual:** Framer Motion. (Spline/Three.js/GSAP only if necessary).
- **Data/API:** TanStack Query, Zod.
- **Data Visualization:** Recharts, ECharts.

## Backend (Render)
- **Primary:** Python + FastAPI.
- **Supporting:** Pydantic, SQLAlchemy, Alembic, httpx.
- **Backup Backend:** Railway.

## Database / Data (Supabase)
- **Primary:** PostgreSQL managed via Supabase.
- **Vector:** pgvector (if RAG is needed).
- **Cache:** Redis (optional, only if needed).
- **Storage:** Supabase Storage (S3-compatible).

## AI
- **Models:** Claude, Gemini. (OpenRouter/Hugging Face as fallbacks).
- **Frameworks:** Vercel AI SDK, LangGraph (only if multi-step/stateful agents are genuinely required).

## Infrastructure / Tools
- **Version Control:** Git + GitHub.
- **Package Managers:** pnpm (JS/TS), uv (Python).
- **Containers:** Docker.
- **Testing:** Pytest (Python), Playwright (E2E), Postman (API).
- **Code Quality:** ESLint, Prettier, Ruff.

## What we are DELIBERATELY NOT using by default
AWS, GCP, Azure, Kubernetes, Kafka, RabbitMQ, Celery, Pinecone, Qdrant, Weaviate, TensorFlow, PyTorch, LangChain, LlamaIndex. (Only activate if the PS strictly demands it).

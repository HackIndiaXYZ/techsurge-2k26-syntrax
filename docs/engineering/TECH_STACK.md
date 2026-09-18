# Final PS-F03 Technology Stack

| Selected technology | Why it is needed |
| --- | --- |
| Next.js, React, TypeScript | Fast, typed dashboard for the judge-visible pipeline |
| Tailwind and shadcn/ui | Accessible, consistent UI without custom component overhead |
| Python, FastAPI, Pydantic | Typed ingestion contracts and deterministic backend logic |
| SQLAlchemy and Alembic | Explicit persistence mapping and controlled schema change |
| PostgreSQL / Supabase | Unique constraints, transactions, telemetry history and audit joins |
| Pytest and Playwright | Core correctness and end-to-end demo rehearsal |
| Vercel / Render | Familiar independent frontend/backend hosting when deployment is needed |
| Docker | Optional local consistency, not a deployment dependency |

Rejected for MVP: Redis/Celery/RabbitMQ/Kafka (no volume need), blockchain (no PS requirement), pgvector/RAG/LLM agent (not in the decision path), Framer Motion (visual polish is lower priority), real UPI/stablecoin rails (forbidden), and microservices (unnecessary integration risk).

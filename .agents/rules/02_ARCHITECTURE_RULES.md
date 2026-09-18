# PS-F03 Architecture Rules

1. Use the documented modular monolith: Next.js UI, FastAPI API, PostgreSQL persistence.
2. Keep validation, consensus, trigger, settlement and audit separate deterministic modules.
3. Do not add microservices, Kafka, blockchain, queues or AI to the critical path without an ADR.
4. Frontend uses documented mock/read models; backend remains source of truth for decisions.

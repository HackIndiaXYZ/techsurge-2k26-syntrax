# SYSTEM ARCHITECTURE — PS-F03

**Status:** ACTIVE
**Owner:** Ramraj (Backend), Akshaya (Infra/DB)
**Updated:** 2026-09-18

---

## Architecture Style

**MODULAR MONOLITH** — Single FastAPI application.

No microservices. No message queues. No event brokers. Simple is correct for 17 hours.

---

## System Diagram

```
┌─────────────────────────────────────────────────────────┐
│  Nikhil — Next.js Frontend (frontend/nikhil)            │
│  Sanju  — AI Module (ai/sanju) [read-only, post-event]  │
└──────────────────────┬──────────────────────────────────┘
                       │ HTTP / JSON
┌──────────────────────▼──────────────────────────────────┐
│                 FastAPI Backend                          │
│  backend/ramraj — Python 3.11+                          │
│                                                         │
│  ┌─────────────────────────────────────────────────┐    │
│  │ POST /telemetry    → Ingestion + Validation      │    │
│  │ POST /simulations  → Full pipeline orchestrator  │    │
│  │ GET  /health                                     │    │
│  │ GET  /policies/{id}                              │    │
│  │ GET  /payouts/{id}                               │    │
│  │ GET  /wallets/{id}                               │    │
│  │ GET  /policies/{id}/audit                        │    │
│  └─────────────────────────────────────────────────┘    │
│                                                         │
│  Services (pure business logic — no external calls):    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  telemetry   │  │  consensus   │  │   trigger    │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  settlement  │  │   wallet     │  │    audit     │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└──────────────────────┬──────────────────────────────────┘
                       │ SQLAlchemy async
┌──────────────────────▼──────────────────────────────────┐
│  PostgreSQL (Supabase or local)                         │
│  Provisioned by Akshaya (infra/akshaya)                 │
│                                                         │
│  Tables:                                                │
│  micro_regions · weather_sources · policies             │
│  trigger_rules · telemetry_events · consensus_results   │
│  trigger_evaluations · payouts · wallets                │
│  wallet_transactions · audit_events                     │
└─────────────────────────────────────────────────────────┘
```

---

## Data Flow (Core Settlement Path)

```
POST /simulations
        │
        ▼
[1] Validate + ingest telemetry for each source
        │  (event_id uniqueness enforced)
        ▼
[2] Consensus evaluation
        │  median(all) → filter |value - median| ≤ 5 mm
        │  quorum check: accepted_count ≥ 2
        ▼
[3] Trigger evaluation
        │  consensus_status == REACHED
        │  AND consensus_value_mm ≥ 100.0
        ▼
[4] Settlement (idempotent)
        │  INSERT INTO payouts
        │  ON CONFLICT (policy_id, trigger_evaluation_id) DO NOTHING
        ▼
[5] Wallet credit (atomic, same transaction)
        │  balance += 1,000,000 paise
        │  INSERT INTO wallet_transactions
        ▼
[6] Audit events written at every step
        │
        ▼
[7] Structured response → Frontend + AI event schema
```

---

## Key Design Decisions

| Decision | Choice | Reason |
|---|---|---|
| Architecture | Modular monolith | 17-hour hackathon; simplicity is correct |
| Language | Python 3.11 | Team stack |
| Framework | FastAPI + Pydantic v2 | Fast, type-safe, OpenAPI built-in |
| ORM | SQLAlchemy async | Required by PROJECT_MEMORY |
| Migrations | Alembic | Required by PROJECT_MEMORY |
| DB | PostgreSQL | Required by PROJECT_MEMORY |
| Money | Integer paise only | Correctness; no floating point |
| Idempotency | DB UNIQUE constraint | Concurrency-safe; application logic alone is not sufficient |
| AI in settlement | FORBIDDEN | Backend is the only financial authority |
| Kafka/Redis/Celery | NOT USED | No documented requirement; over-engineering |
| Blockchain | NOT USED | No requirement; out of scope |

---

## Ownership Boundaries

| Area | Owner |
|---|---|
| FastAPI application, all services, backend API | Ramraj |
| PostgreSQL provisioning, DDL execution, migrations in shared DB | Akshaya |
| Next.js frontend, all UI | Nikhil |
| AI explanation module (post-settlement, read-only) | Sanju |

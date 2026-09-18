# MVP SCOPE — PS-F03

**Status:** ACTIVE
**Updated:** 2026-09-18
**Owner:** Ramraj (Backend)

---

## In-Scope for PS-F03 MVP Demo

| Feature | Status |
|---|---|
| 3-source simulated rainfall ingestion | ✅ In scope |
| Telemetry validation (metric, unit, value, source, region) | ✅ In scope |
| Deduplication (event_id uniqueness, DB-enforced) | ✅ In scope |
| Deterministic consensus (median, quorum=2, tolerance=5mm) | ✅ In scope |
| Deterministic trigger (rainfall ≥ 100mm) | ✅ In scope |
| Idempotent settlement (DB UniqueConstraint) | ✅ In scope |
| Synthetic wallet (integer paise, ledger) | ✅ In scope |
| Append-only audit trail | ✅ In scope |
| Simulation endpoint (full pipeline) | ✅ In scope |
| Four demo scenarios (Normal, Corrupted, No-consensus, Duplicate) | ✅ In scope |
| FastAPI REST API with OpenAPI docs | ✅ In scope |
| API contracts for Nikhil (frontend) | ✅ In scope |
| AI event schema for Sanju (post-settlement, read-only) | ✅ In scope (schema defined, delivery TBD) |
| Integration tests (12 critical scenarios) | ✅ In scope |
| Alembic migration for schema | ✅ In scope |
| Demo seed data (region, sources, policy, wallet) | ✅ In scope |

## Out-of-Scope for MVP

| Feature | Status |
|---|---|
| Real money / real payments / real UPI | ❌ Out of scope |
| Real bank account or real wallet | ❌ Out of scope |
| Production weather API integration | ❌ Out of scope |
| Blockchain / distributed ledger | ❌ Out of scope |
| Message queues (Kafka, RabbitMQ, Celery) | ❌ Out of scope |
| Multi-region / multi-policy support | ❌ Out of scope (one region, one policy for demo) |
| Authentication / JWT / OAuth | ❌ TBD (document as TBD, not implemented for MVP) |
| AI/LLM settlement authority | ❌ FORBIDDEN (not merely out of scope) |
| Real-time WebSocket updates | ❌ Out of scope (polling is sufficient) |
| Production monitoring / alerting | ❌ Out of scope |
| Multi-tenant support | ❌ Out of scope |

## Frozen Demo Scenarios

| Scenario | Input | Expected |
|---|---|---|
| NORMAL | A=110, B=108, C=111 | Consensus 110mm → triggered → 1 payout → ₹10,000 |
| CORRUPTED_SOURCE | A=110, B=108, C=7 | C outlier → A/B consensus 109mm → triggered → 1 payout |
| NO_CONSENSUS | A=120, B=50, C=5 | Only B in tolerance → quorum fail → NO payout |
| DUPLICATE_REPLAY | Same valid scenario × N | Exactly 1 wallet credit regardless of N |

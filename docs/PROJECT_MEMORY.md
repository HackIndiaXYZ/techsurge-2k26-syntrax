# SYNTRAX Project Memory

## Current source of truth

**Official PS requirement:** TechSurge 2K26 / Kalachakra PS-F03 is *Autonomous Parametric Climate Insurance & Instant Settlement Engine*. The official flow is multi-source telemetry ingestion, validation/consensus, deterministic trigger evaluation, idempotent payout execution, and an audit trail. The prototype must work with public or synthetic weather data and synthetic wallets; no real money, accounts, payment rails, or provider contracts are allowed.

**Team design decision:** Build one small, transparent vertical slice: a rainfall policy for a synthetic micro-region, three simulated sources, 2-of-3 consensus, deterministic evaluation, and a PostgreSQL-backed synthetic wallet ledger. The detailed rationale is in [PS Analysis](round2/PS_ANALYSIS.md).

**Team assumption:** The effective build window is approximately 17 hours. Time-sensitive design decisions therefore favor a modular monolith over distributed infrastructure.

## Product boundary

This is not an insurer, wallet, UPI application, or production payment system. It simulates a parametric payout and shows evidence explaining why it happened. Basis risk, false triggers, and missed triggers are explicit limitations.

## Canonical MVP

`telemetry -> validation -> consensus -> trigger evaluation -> payout instruction -> synthetic wallet credit -> audit event`

The canonical entity definitions are in [Data Model](database/DATA_MODEL.md). No other document may redefine those entities.

## Team and branches

| Owner | Responsibility | Branch |
| --- | --- | --- |
| Nikhil | Frontend, product experience, integration lead | `frontend/nikhil` |
| Ramraj | Backend and financial systems | `backend/ramraj` |
| Sanju | AI/ML, agents, RAG evaluation | `ai/sanju` |
| Akshaya | Infrastructure, database, security, testing | `infra/akshaya` |

`main` is the stable integration branch. Contracts are agreed before parallel implementation; see [Git Workflow](engineering/GIT_WORKFLOW.md).

## Historical note

The Round 1 NEXTRA employment-direction concept is historical only. It is retained in `docs/history/` to preserve team context and must not influence PS-F03 implementation.

# SYNTRAX PS-F03 Knowledge Base

The repository is the team source of truth. The official problem PDF is recorded in [Source Material Index](reference/SOURCE_MATERIAL_INDEX.md). Every requirement below is explicitly classified as organizer requirement, verified fact, team design decision, team assumption, optional idea, or out of scope.

## Start here

1. [Project Memory](PROJECT_MEMORY.md) - scope, safety boundary, and canonical flow.
2. [Problem Statement](round2/PROBLEM_STATEMENT.md) and [PS Analysis](round2/PS_ANALYSIS.md) - official requirements separated from decisions.
3. [MVP Scope](round2/MVP_SCOPE.md) - what must be built in 17 hours.
4. [Data Model](database/DATA_MODEL.md), [API Contracts](architecture/API_CONTRACTS.md), and [System Architecture](architecture/SYSTEM_ARCHITECTURE.md) - build contracts.
5. [Demo Strategy](hackathon/DEMO_STRATEGY.md) and [Testing Strategy](testing/TESTING_STRATEGY.md) - prove the flow and failure modes.

## Core build contracts

- [Policy Model](architecture/POLICY_MODEL.md), [Weather Telemetry](architecture/WEATHER_TELEMETRY.md), and [Consensus and Trigger Engine](architecture/CONSENSUS_AND_TRIGGER_ENGINE.md)
- [Synthetic Payout Architecture](fintech/PAYMENT_ARCHITECTURE.md), [Idempotency](fintech/IDEMPOTENCY.md), [Synthetic Wallet](fintech/SYNTHETIC_WALLET.md), and [Audit Trail](fintech/AUDIT_TRAIL.md)
- [Failure Injection and Metrics](testing/FAILURE_INJECTION_AND_METRICS.md), [Evaluation Traceability](hackathon/EVALUATION_TRACEABILITY.md), and [Production Gap](fintech/PRODUCTION_GAP.md)

## Areas

| Area | Use it for |
| --- | --- |
| `round2/` | PS-F03 requirements, scope, personas, acceptance criteria |
| `architecture/` | components, data flow, API, consensus and trigger decisions |
| `database/` | canonical entities, PostgreSQL schema, seeds and ownership |
| `fintech/` | parametric-insurance concepts, payout simulation, risk framing |
| `ai/` | optional support only; deterministic payment boundary |
| `engineering/` | ownership, contracts, integration, development rules |
| `security/` | prototype controls and production gaps |
| `testing/` | scenario matrix, metrics, demo rehearsal |
| `deployment/` | small deployment plan and environment rules |
| `hackathon/` | 17-hour plan, judge flow, traceability |
| `decisions/` | assumptions, tradeoffs, ADRs, unresolved items |
| `operations/` | handoffs, blocker and release templates |
| `reference/` | terminology, sources, quick reference |
| `history/` | explicitly historical Round 1 record |

See [Document Inventory](DOCUMENT_INVENTORY.md) for the classification and intended use of every pre-existing documentation file.

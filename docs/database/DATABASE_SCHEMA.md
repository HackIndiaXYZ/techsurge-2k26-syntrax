# TerraFlux Database Schema

> **STATUS:** Implemented  
> **OWNER:** Akshaya (Infra)  
> **SUPABASE PROJECT:** syntrax (`qdnwxtncipqbjreuzoxl`)

## Architecture Boundary

PostgreSQL/Supabase is the **durable persistence layer**. It is responsible for:

- Referential integrity
- Uniqueness / idempotency enforcement
- Transaction safety
- Financial consistency (integer paise, atomic settlement)
- Auditability
- Access control (RLS)

The database does **NOT** execute:
- Weather consensus logic (backend)
- Financial trigger evaluation (backend)
- AI/ML inference (AI layer)
- Settlement authorization (backend)

---

## Money Representation

All monetary values are stored as **`bigint` (paise)**.

| Display   | Storage        | Column Type |
|-----------|----------------|-------------|
| ₹10,000   | `1000000`      | `bigint`    |
| ₹0.01     | `1`            | `bigint`    |

Telemetry values (rainfall, temperature) use `numeric` for decimal precision.

---

## Tables (14)

### Lookup / Reference

| # | Table              | Purpose                                |
|---|--------------------|----------------------------------------|
| 1 | `policyholders`    | Synthetic demo policyholders           |
| 2 | `micro_regions`    | Geographic micro-regions               |
| 3 | `weather_sources`  | Known telemetry provider identities    |
| 4 | `trigger_rules`    | Versioned deterministic trigger defs   |

### Core Domain

| # | Table                          | Purpose                                      |
|---|--------------------------------|----------------------------------------------|
| 5 | `policies`                     | Policy linking holder, region, trigger rule   |
| 6 | `telemetry_events`             | Raw/normalized weather observations           |
| 7 | `telemetry_validation_results` | Validation evidence records                   |
| 8 | `consensus_results`            | Multi-source consensus outcomes               |
| 9 | `consensus_members`            | Telemetry participation in consensus          |
| 10| `trigger_evaluations`          | Deterministic policy trigger evaluation       |

### Financial

| # | Table                 | Purpose                            |
|---|-----------------------|------------------------------------|
| 11| `wallets`             | Synthetic demo wallets             |
| 12| `payouts`             | Settlement intent and lifecycle    |
| 13| `wallet_transactions` | Immutable wallet ledger            |

### Audit

| # | Table          | Purpose                         |
|---|----------------|---------------------------------|
| 14| `audit_events` | Immutable system evidence trail |

---

## Enum Types

| Type                    | Values                                                          |
|-------------------------|-----------------------------------------------------------------|
| `validation_state`      | PENDING, ACCEPTED, REJECTED, DUPLICATE                         |
| `consensus_state`       | PENDING, ACHIEVED, NO_CONSENSUS, EXPIRED                       |
| `consensus_role`        | ACCEPTED, OUTLIER, REJECTED                                    |
| `trigger_outcome`       | TRIGGERED, NOT_MET, NOT_ELIGIBLE, NO_CONSENSUS, ALREADY_TRIGGERED, EXPIRED |
| `policy_status`         | DRAFT, ACTIVE, EXPIRED, CANCELLED, SUSPENDED                  |
| `wallet_status`         | ACTIVE, SUSPENDED, CLOSED                                      |
| `payout_state`          | PENDING, PROCESSING, COMPLETED, FAILED, CANCELLED             |
| `transaction_direction` | CREDIT, DEBIT                                                  |
| `trigger_operator`      | GTE, GT, LTE, LT, EQ                                          |

---

## Idempotency (4 Layers)

| Layer                    | Constraint                                    | Table                 |
|--------------------------|-----------------------------------------------|-----------------------|
| Telemetry ingestion      | `unique(source_id, source_event_id)`          | `telemetry_events`    |
| Payout per policy        | `unique(policy_id)`                           | `payouts`             |
| Settlement execution key | `unique(idempotency_scope, idempotency_key)`  | `payouts`             |
| Wallet transaction       | `unique(payout_id)`                           | `wallet_transactions` |

---

## Foreign Key Deletion Semantics

All financial and audit foreign keys use `ON DELETE RESTRICT`.

**No cascade deletion** on: policies, payouts, wallet_transactions, audit_events.

---

## Row Level Security (RLS)

RLS is enabled on all 14 tables.

| Role            | Permission                                           |
|-----------------|------------------------------------------------------|
| `anon`          | SELECT on `micro_regions`, `weather_sources` only    |
| `authenticated` | SELECT on all tables                                 |
| `service_role`  | Bypasses RLS (full read/write for backend)           |

**No anonymous financial writes are possible.**

---

## Indexes

| Table                          | Index                                              |
|--------------------------------|----------------------------------------------------|
| `policies`                     | `(region_id, status, start_at, end_at)`            |
| `telemetry_events`             | `(region_id, metric, window_end, validation_state)`|
| `telemetry_validation_results` | `(telemetry_event_id)`                             |
| `audit_events`                 | `(correlation_id, occurred_at)`                    |
| `audit_events`                 | `(entity_type, entity_id, occurred_at)`            |

---

## Atomic Settlement Sequence

```
BEGIN
  Lock payout row (SELECT FOR UPDATE)
  If payout already COMPLETED → return duplicate indication
  Lock wallet row (SELECT FOR UPDATE)
  INSERT wallet_transaction (unique(payout_id) prevents duplicates)
  UPDATE wallet balance
  UPDATE payout state → COMPLETED
  INSERT audit_event
COMMIT
```

---

## Seed Data

| Entity          | ID                                           | Value                    |
|-----------------|----------------------------------------------|--------------------------|
| Policyholder    | `a1000000-0000-0000-0000-000000000001`       | Ravi Kumar (Synthetic)   |
| Micro-Region    | `b2000000-0000-0000-0000-000000000001`       | Kurnool Synthetic        |
| Source A        | `c3000000-0000-0000-0000-000000000001`       | SYN-SRC-A                |
| Source B        | `c3000000-0000-0000-0000-000000000002`       | SYN-SRC-B                |
| Source C        | `c3000000-0000-0000-0000-000000000003`       | SYN-SRC-C                |
| Trigger Rule    | `d4000000-0000-0000-0000-000000000001`       | RAINFALL ≥ 100mm / 60min |
| Policy          | `e5000000-0000-0000-0000-000000000001`       | Active, ₹10,000 payout   |
| Wallet          | `f6000000-0000-0000-0000-000000000001`       | INR, balance ₹0          |

---

## Basis Risk Notice

> "The prototype settles against a predefined weather index; the index does not guarantee that the payout equals the policyholder's actual loss."

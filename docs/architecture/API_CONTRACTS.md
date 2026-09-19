# PS-F03 API CONTRACTS

**Status:** ACTIVE — Established for PS-F03 implementation on `backend/ramraj`.
**Owner:** Ramraj (Backend)
**Consumers:** Nikhil (Frontend), Sanju (AI — read-only, post-settlement)
**Base URL (dev):** `http://localhost:8000`
**Base URL (prod):** TBD — provisioned by Akshaya on Render.

---

## Global Conventions

- All requests/responses use `application/json`
- All timestamps are ISO 8601 UTC strings: `"2026-09-18T11:30:00Z"`
- All monetary amounts are **integer paise** (₹1 = 100 paise; ₹10,000 = 1,000,000 paise)
- **Never use floating point** for monetary values
- Errors follow the standard error envelope below
- `correlation_id` is a ULID string included in every response for tracing

### Standard Error Envelope

```json
{
  "error": "VALIDATION_ERROR",
  "message": "Human-readable description",
  "details": {}
}
```

| HTTP Status | Meaning |
|---|---|
| 200 | Success |
| 201 | Created |
| 400 | Bad request / malformed payload |
| 404 | Entity not found |
| 409 | Conflict (e.g., already settled) |
| 422 | Pydantic validation error |
| 500 | Unexpected internal server error |

---

## Endpoints

---

### `GET /health`

Health check. Returns backend status and DB connectivity.

**Request:** None

**Response 200:**
```json
{
  "status": "ok",
  "environment": "development",
  "database": "connected"
}
```

**Response 500** (DB unreachable):
```json
{
  "status": "degraded",
  "environment": "development",
  "database": "error"
}
```

---

### `POST /telemetry`

Ingest a single rainfall telemetry observation from a simulated weather source.
Backend validates, deduplicates, and persists. Does NOT automatically trigger settlement.
Settlement is initiated via `POST /simulations` during demo.

**Request body:**
```json
{
  "event_id": "01J8ZXXXXXXXXXXXXXXXXXXXXXX",
  "source_id": "source-a",
  "region_id": "region-kaveri-delta",
  "observed_at": "2026-09-18T11:00:00Z",
  "metric": "rainfall",
  "value": 110.0,
  "unit": "mm"
}
```

| Field | Type | Required | Notes |
|---|---|---|---|
| `event_id` | string | YES | Client-generated unique ID (ULID recommended) |
| `source_id` | string | YES | Must match a registered WeatherSource |
| `region_id` | string | YES | Must match a registered MicroRegion |
| `observed_at` | ISO 8601 string | YES | When the measurement was taken |
| `metric` | string | YES | Must be `"rainfall"` for PS-F03 MVP |
| `value` | number | YES | Rainfall in mm. Must be ≥ 0 |
| `unit` | string | YES | Must be `"mm"` |

**Response 201 — Accepted:**
```json
{
  "status": "ACCEPTED",
  "event_id": "01J8ZXXXXXXXXXXXXXXXXXXXXXX",
  "correlation_id": "01J8ZYYYYYYYYYYYYYYYYYYYYYY",
  "received_at": "2026-09-18T11:00:01Z"
}
```

**Response 200 — Duplicate (idempotent):**
```json
{
  "status": "DUPLICATE",
  "event_id": "01J8ZXXXXXXXXXXXXXXXXXXXXXX",
  "correlation_id": "01J8ZYYYYYYYYYYYYYYYYYYYYYY",
  "message": "Event already ingested. Ignored."
}
```

**Response 400** — Invalid metric/unit/value:
```json
{
  "error": "INVALID_TELEMETRY",
  "message": "Unsupported metric: temperature. Only 'rainfall' is accepted.",
  "details": {}
}
```

---

### `POST /simulations`

Run a complete end-to-end PS-F03 pipeline for a controlled weather scenario.
This is the primary demo endpoint.

The simulation submits weather observations for all three sources through the
real pipeline: ingestion → validation → deduplication → consensus → trigger →
settlement → wallet → audit.

**Request body:**
```json
{
  "scenario": "NORMAL",
  "policy_id": "policy-kaveri-2026",
  "region_id": "region-kaveri-delta",
  "observations": [
    {"source_id": "source-a", "value": 110.0},
    {"source_id": "source-b", "value": 108.0},
    {"source_id": "source-c", "value": 111.0}
  ],
  "observed_at": "2026-09-18T11:00:00Z"
}
```

| Field | Type | Notes |
|---|---|---|
| `scenario` | enum | `NORMAL` \| `CORRUPTED_SOURCE` \| `NO_CONSENSUS` \| `DUPLICATE_REPLAY` |
| `policy_id` | string | Must match a seeded policy |
| `region_id` | string | Must match a seeded region |
| `observations` | array | One per source. `source_id` + `value` (mm) |
| `observed_at` | ISO 8601 | Observation window anchor timestamp |

**Response 200:**
```json
{
  "correlation_id": "01J8ZYYYYYYYYYYYYYYYYYYYYYY",
  "scenario": "NORMAL",
  "policy_id": "policy-kaveri-2026",

  "telemetry": {
    "submitted": 3,
    "accepted": 3,
    "rejected": 0,
    "duplicates": 0,
    "observations": [
      {"source_id": "source-a", "value": 110.0, "status": "ACCEPTED"},
      {"source_id": "source-b", "value": 108.0, "status": "ACCEPTED"},
      {"source_id": "source-c", "value": 111.0, "status": "ACCEPTED"}
    ]
  },

  "consensus": {
    "status": "REACHED",
    "median_all_sources": 110.0,
    "consensus_value_mm": 110.0,
    "accepted_sources": ["source-a", "source-b", "source-c"],
    "outlier_sources": []
  },

  "trigger": {
    "status": "TRIGGERED",
    "threshold_mm": 100.0,
    "consensus_value_mm": 110.0,
    "reason": "Consensus rainfall 110.0 mm >= threshold 100.0 mm"
  },

  "settlement": {
    "status": "SUCCESS",
    "payout_id": "01J8PXXXXXXXXXXXXXXXXXXXXXX",
    "idempotency_status": "NEW",
    "payout_amount_paise": 1000000,
    "payout_amount_inr_display": "₹10,000"
  },

  "wallet": {
    "wallet_id": "wallet-kaveri-2026",
    "balance_before_paise": 0,
    "balance_after_paise": 1000000,
    "credited": true
  },

  "audit_id": "01J8AXXXXXXXXXXXXXXXXXXXXXX",

  "latency": {
    "observed_at": "2026-09-18T11:00:00Z",
    "received_at": "2026-09-18T11:00:01.123Z",
    "trigger_evaluated_at": "2026-09-18T11:00:01.145Z",
    "payout_completed_at": "2026-09-18T11:00:01.201Z",
    "detection_latency_ms": 22,
    "settlement_latency_ms": 56,
    "end_to_end_latency_ms": 78
  }
}
```

**No-consensus response example (HTTP 200 — business result, not server error):**
```json
{
  "correlation_id": "...",
  "scenario": "NO_CONSENSUS",
  "consensus": {
    "status": "NO_CONSENSUS",
    "reason": "Only 1 source(s) within tolerance. Quorum requires 2."
  },
  "trigger": {
    "status": "TRIGGER_BLOCKED_NO_CONSENSUS",
    "reason": "No authoritative consensus established."
  },
  "settlement": {
    "status": "SKIPPED",
    "reason": "Trigger blocked. No payout."
  },
  "wallet": {
    "credited": false
  }
}
```

**Duplicate replay response example (HTTP 200):**
```json
{
  "correlation_id": "...",
  "scenario": "DUPLICATE_REPLAY",
  "settlement": {
    "status": "DUPLICATE",
    "idempotency_status": "ALREADY_SETTLED",
    "payout_id": "01J8PXXXXXXXXXXXXXXXXXXXXXX",
    "reason": "Settlement already completed for this policy+trigger. No wallet credit."
  },
  "wallet": {
    "credited": false
  }
}
```

---

### `GET /policies/{policy_id}`

Retrieve a parametric policy definition.

**Response 200:**
```json
{
  "policy_id": "policy-kaveri-2026",
  "region_id": "region-kaveri-delta",
  "status": "ACTIVE",
  "trigger_metric": "rainfall",
  "trigger_threshold_mm": 100.0,
  "trigger_operator": ">=",
  "observation_window_minutes": 60,
  "payout_amount_paise": 1000000,
  "payout_amount_inr_display": "₹10,000",
  "currency": "INR",
  "valid_from": "2026-09-01T00:00:00Z",
  "valid_until": "2026-12-31T23:59:59Z"
}
```

**Response 404:**
```json
{
  "error": "NOT_FOUND",
  "message": "Policy policy-kaveri-2026 not found."
}
```

---

### `GET /payouts/{payout_id}`

Retrieve a payout record by ID.

**Response 200:**
```json
{
  "payout_id": "01J8PXXXXXXXXXXXXXXXXXXXXXX",
  "policy_id": "policy-kaveri-2026",
  "trigger_evaluation_id": "01J8TXXXXXXXXXXXXXXXXXXXXXX",
  "status": "SUCCESS",
  "amount_paise": 1000000,
  "amount_inr_display": "₹10,000",
  "idempotency_key": "policy-kaveri-2026::01J8TXXXXXXXXXXXXXXXXXXXXXX",
  "created_at": "2026-09-18T11:00:01Z",
  "completed_at": "2026-09-18T11:00:01Z"
}
```

---

### `GET /wallets/{wallet_id}`

Retrieve synthetic wallet balance and recent transactions.

**Response 200:**
```json
{
  "wallet_id": "wallet-kaveri-2026",
  "policy_id": "policy-kaveri-2026",
  "balance_paise": 1000000,
  "balance_inr_display": "₹10,000",
  "currency": "INR",
  "transactions": [
    {
      "transaction_id": "01J8WXXXXXXXXXXXXXXXXXXXXXX",
      "payout_id": "01J8PXXXXXXXXXXXXXXXXXXXXXX",
      "amount_paise": 1000000,
      "balance_before_paise": 0,
      "balance_after_paise": 1000000,
      "created_at": "2026-09-18T11:00:01Z"
    }
  ]
}
```

---

### `GET /policies/{policy_id}/audit`

Retrieve audit trail for a policy (most recent first).

**Query params:**
- `limit` (int, default 50)

**Response 200:**
```json
{
  "policy_id": "policy-kaveri-2026",
  "total": 7,
  "events": [
    {
      "audit_id": "01J8AXXXXXXXXXXXXXXXXXXXXXX",
      "event_type": "WALLET_CREDITED",
      "entity_type": "WALLET",
      "entity_id": "wallet-kaveri-2026",
      "correlation_id": "01J8ZYYYYYYYYYYYYYYYYYYYYYY",
      "status": "SUCCESS",
      "metadata": {
        "amount_paise": 1000000,
        "balance_after_paise": 1000000
      },
      "created_at": "2026-09-18T11:00:01Z"
    }
  ]
}
```

---

## AI Integration Boundary (TBD)

After settlement, the backend can expose a structured settlement event for Sanju's AI module.
The delivery mechanism (webhook / polling endpoint / DB read) is **TBD** — to be agreed with Sanju.

Candidate event schema available at `POST /simulations` response.
AI may NOT be called during the settlement decision path.

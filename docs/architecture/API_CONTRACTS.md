# PS-F03 API Contracts

All timestamps are RFC 3339 UTC strings. IDs are UUIDs unless a fixture uses a readable display code. Errors use `{ "code", "message", "correlation_id" }`; no internal stack trace is returned.

## Telemetry

`POST /v1/telemetry/events` accepts:

```json
{
  "source_id": "uuid", "source_event_id": "source-a-001", "region_id": "uuid",
  "metric": "RAINFALL_MM", "observed_at": "2026-09-18T10:00:00Z",
  "window_start": "2026-09-18T09:00:00Z", "window_end": "2026-09-18T10:00:00Z",
  "value": 101.0, "unit": "mm", "metadata": {"scenario": "clean"}
}
```

Return `202` with `event_id`, `validation_state`, and `correlation_id` for a new event. Return `200` with the original result and `validation_state: DUPLICATE` when `(source_id, source_event_id)` was already processed. Return `400` for schema/range errors, `401` for absent demo source credential, `409` for incompatible replay, and `429` when rate limited.

## Read models

| Method and path | Response purpose |
| --- | --- |
| `GET /v1/policies` and `GET /v1/policies/{policy_id}` | Active policy, trigger rule and latest evaluation |
| `GET /v1/regions/{region_id}/consensus?window_end=` | Member readings, rejected sources, quorum and consensus state |
| `GET /v1/policies/{policy_id}/trigger-evaluations` | Deterministic evaluation history |
| `GET /v1/payouts/{payout_id}` | Payout state, idempotency key, timestamps and transaction ID |
| `GET /v1/wallets/{wallet_id}` | Synthetic balance and transaction list |
| `GET /v1/audit-events?correlation_id=` | Ordered evidence for one scenario |
| `GET /v1/dashboard` | Small read model for one-second frontend polling |

## Simulation-only commands

`POST /v1/simulations/{scenario}` supports only the documented seeded scenarios: `normal`, `corrupted-source`, `clean-trigger`, `duplicate-event`, `missing-source`, and `payout-retry`. Require an operator demo token. The response returns a `correlation_id`; these routes must not exist in a production deployment without replacement controls.

## Settlement idempotency

`POST /v1/payouts/{payout_id}/execute` requires `Idempotency-Key`. The server stores `(scope='PAYOUT_EXECUTE', key)` before/with the transaction. Same key plus same request returns the original payout response; same key plus different payload returns `409 IDEMPOTENCY_KEY_REUSED`.

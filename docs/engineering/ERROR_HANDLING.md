# Error Handling

Use stable machine codes: `INVALID_SCHEMA`, `INVALID_UNIT`, `STALE_EVENT`, `FUTURE_EVENT`, `IMPOSSIBLE_VALUE`, `DUPLICATE_EVENT`, `NO_CONSENSUS`, `POLICY_INACTIVE`, `POLICY_EXPIRED`, `ALREADY_TRIGGERED`, `IDEMPOTENCY_KEY_REUSED`, and `PAYOUT_FAILED`. Return a correlation ID. Persist material rejections and failures in audit events; do not silently drop an event.

Never retry a non-idempotent mutation with a new key automatically. A failed payout retry reuses the original payout and idempotency key.

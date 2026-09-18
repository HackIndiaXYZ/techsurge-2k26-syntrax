# PS-F03 API Rules

1. Implement only endpoints in `docs/architecture/API_CONTRACTS.md` or update that contract first.
2. Validate telemetry server-side; use stable errors and correlation IDs.
3. Payout execution requires an idempotency key. Simulation routes require a demo operator token and remain synthetic-only.
4. Frontend and optional AI work against fixtures until contract integration is ready.

# API Testing

Contract tests validate every telemetry field, error code, status code, authentication assumption, and idempotency response in [API Contracts](../architecture/API_CONTRACTS.md). Tests submit the same source event twice, submit an idempotency key twice, and submit the same key with a changed payload. Read endpoints must return only the canonical field names.

Use FastAPI test client with a transaction-isolated database. Do not call a weather provider or payment API from automated tests.

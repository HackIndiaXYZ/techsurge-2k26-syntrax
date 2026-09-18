# Webhooks

**Status: not needed for MVP.** Simulated sources submit directly to telemetry ingestion and the dashboard polls read APIs. If a future provider webhook is introduced, verify a signature, timestamp/replay window, source identity, schema, idempotency and audit correlation before processing. Never accept an unauthenticated hook as a trusted oracle.

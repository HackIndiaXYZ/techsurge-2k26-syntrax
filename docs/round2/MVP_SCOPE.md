# PS-F03 MVP Scope

## Must build

- One active synthetic rainfall policy and one synthetic policyholder wallet.
- Three simulated/public-shaped telemetry sources for one synthetic micro-region.
- Schema validation, deduplication, freshness/range checks, 2-of-3 consensus, and visible rejected-source reason.
- Deterministic trigger evaluation, one idempotent simulated payout, double-entry-like wallet transaction record, and append-only audit events.
- Dashboard screens for the policy-to-audit story, failure injection, and latency measurement.

## Should build

- Seeded normal, flood, missing-source, outlier, duplicate, and retry scenarios.
- PostgreSQL persistence, one-click demo reset, OpenAPI output, and a deployed frontend/backend.

## Only if time

- Read-only policyholder view, SSE instead of one-second polling, offline anomaly score, downloadable audit evidence, or a public data comparison.

## Do not build

- Real payment integration, real accounts, blockchain, Kafka, microservices, Celery/RabbitMQ, real insurer onboarding, liquidity rebalancing, stablecoin routing, autonomous LLM payouts, or excessive animation.

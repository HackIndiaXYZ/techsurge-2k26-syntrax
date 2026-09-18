# PS-F03 Implementation Requirements

## Functional requirements

1. Accept a canonical `TelemetryEvent` and store its validation outcome exactly once.
2. Deduplicate by source event ID and return a stable result for retry.
3. Build a consensus result only from valid, distinct sources in the same region, metric, and measurement bucket.
4. Evaluate only active policies whose region, metric, and window match a confirmed consensus.
5. Create at most one payout per triggered policy; retrying a payout request must never create a second wallet credit.
6. Persist an audit event for each material transition.

## Non-functional prototype requirements

Use server-side UTC timestamps, structured error codes, bounded input sizes, and tested scenario fixtures. Measure actual end-to-end settlement latency; do not promise a number in documentation. Expose synthetic status labels visibly so the demo cannot be mistaken for a real financial service.

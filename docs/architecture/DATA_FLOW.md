# PS-F03 Data Flow

1. A source submits a `TelemetryEvent` with source event ID, region, metric, observed timestamp, value, unit, and metadata.
2. Ingestion assigns `received_at`, normalizes the unit, validates range/freshness, computes a fingerprint, and either stores an accepted/rejected event or returns the earlier duplicate result.
3. Consensus selects valid readings from enabled, distinct sources for the same `(region_id, metric, window_start, window_end)`. It records members, outliers, quorum and value.
4. The trigger engine evaluates matching active policies using only the persisted consensus result. It records every result, including no-consensus, expired, already-triggered, and not-met states.
5. An eligible evaluation creates a payout with an idempotency key. Settlement atomically inserts one wallet credit and marks payout completed, then writes audit events.
6. Read APIs return correlated IDs so the dashboard can reconstruct the causal chain.

No client event skips a persisted transition, and no payout is created from raw telemetry alone.

# PS-F03 Acceptance Criteria

The MVP is acceptable when a judge can trace one active policy from three incoming readings to a single synthetic wallet credit, and can answer “why did this payout happen?” from retained evidence.

| Criterion | Pass evidence |
| --- | --- |
| Corrupted telemetry is handled | One outlier shows a rejection reason; the consensus member set is visible |
| Valid consensus is deterministic | Identical seeded inputs produce the same value and trigger result |
| Policy trigger is constrained | Inactive, expired, unmatched-region, no-consensus, and already-triggered policies do not pay |
| Payout is idempotent | Retry uses the same idempotency key and produces one `wallet_transactions` credit |
| Responsible framing is visible | Synthetic wallet/payout and basis-risk limitation appear in the UI and demo |
| Latency is measured | Stored T0/T1/T2 timestamps and at least repeated trial results |

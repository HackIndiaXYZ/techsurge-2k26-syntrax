# Failure Injection and Metrics

## Controlled judge demonstration

Use a validation-only preview to send source A=101, B=102 and C=500 mm for the same synthetic window. Show C rejected as an impossible/disagreeing input according to the persisted reason. Then reset or start the active clean scenario and send A=101, B=102, C=103. The 2-of-3-or-better quorum produces median 102 mm; against a 100 mm policy it triggers exactly once. Invoke payout retry with the original idempotency key and show no second transaction.

## Latency protocol

Set `T0` when a consensus is persisted and the policy evaluation records `TRIGGERED`; `T1` when payout processing starts; and `T2` when the wallet transaction and payout completion commit. Use backend UTC clock timestamps, record the correlation ID, run the clean scenario repeatedly, and report count, mean, and optional p95 of `T2 - T0`. The UI displays per-run latency; the pitch reports the measured aggregate and environment. Never use browser-render timing as settlement latency.

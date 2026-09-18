# PS-F03 Testing Rules

1. Prioritize telemetry validation, consensus, trigger, payout transaction, audit evidence and UI trace tests.
2. Required scenarios: normal, one outlier, impossible/malformed/stale, no quorum, duplicate telemetry, duplicate trigger/payout, timeout/retry and basis risk.
3. Measure T0/T1/T2 from server records. Demo readiness requires the failure-injection and idempotency replay to pass.

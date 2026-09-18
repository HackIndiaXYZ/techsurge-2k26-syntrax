# PS-F03 Quick Reference

- Policy: `RAINFALL_MM >= 100 mm` in a `60-minute` window; INR `10,000` synthetic payout once.
- Sources: 3; quorum: 2; agreement tolerance: 5 mm; value: median of agreeing group.
- Payout guardrails: unique policy payout, unique wallet transaction per payout, idempotency key, transaction boundary.
- Demo values: corrupt preview `101,102,500`; clean trigger `101,102,103` -> consensus `102`.
- Required labels: `SYNTHETIC`, `SIMULATED PAYOUT`, `NO REAL MONEY`, `BASIS RISK`.
- Read first: Data Model, API Contracts, Consensus and Trigger Engine, Demo Strategy.

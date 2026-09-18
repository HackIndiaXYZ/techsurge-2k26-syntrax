# PS-F03 Component Map

| Component | Owns | Does not own |
| --- | --- | --- |
| Telemetry ingestion | Canonical event parsing, validation and deduplication | Deciding policy eligibility |
| Consensus service | Source grouping, quorum, consensus value and rejection reasons | Paying or altering a policy |
| Trigger engine | Pure policy-to-consensus eligibility evaluation | LLM judgement or wallet mutation |
| Settlement service | Payout state machine, idempotency key and wallet transaction | Real payment rails |
| Audit service | Correlated append-only evidence records | Business decision overrides |
| Simulation service | Seeded scenarios and safe retry injection | Production weather/provider integration |
| Next.js dashboard | State visualization and operator controls | Trusting client-side calculations |

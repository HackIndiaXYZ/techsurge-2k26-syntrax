# PS-F03 Terminology

| Term | Plain meaning | Technical meaning here |
| --- | --- | --- |
| Oracle | A source of external facts | A logical weather source adapter, not blockchain infrastructure |
| Telemetry | A recorded measurement | One canonical weather event with source, time, region, metric and unit |
| Validation | Basic trust checks | Schema, source, range, unit, freshness and duplicate checks |
| Consensus | Agreement among sources | 2-of-3 within 5 mm, median of agreeing values |
| Trigger | Pre-agreed event that enables payout | Rainfall consensus >= policy threshold in policy window |
| Idempotency | Safe repeat of a request | Same payout key yields original result and one wallet credit |
| Audit trail | Evidence of what happened | Correlated immutable-like records for each material step |
| Basis risk | Parameter and real loss differ | False trigger or missed trigger in synthetic labels |
| Latency | Time between stages | T2 payout completion minus T0 confirmed trigger condition |

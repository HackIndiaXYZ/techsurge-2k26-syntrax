# PS-F03 Evaluation Traceability Matrix

| PS evaluation focus | System component | Implementation proof | Test / demo evidence |
| --- | --- | --- | --- |
| Problem understanding | Policy and terminology | Rainfall policy and explicit basis-risk notes | Judge policy walkthrough |
| Oracle consensus | Validation and consensus service | 3 sources, 2-of-3 median, reasons | Corrupt 500 mm source preview |
| Idempotent settlement | Payout/ledger transaction | Unique policy payout, key, transaction | Retry creates no extra credit |
| Latency and reliability | Timestamped backend flow | T0/T1/T2 stored per correlation | Repeated clean-trigger trials |
| Adversarial resilience | Input validation/deduplication | stale, malformed, impossible, duplicate checks | Failure test matrix |
| Responsible fintech | Synthetic-only boundaries | labels and no-real-rail design | UI disclaimer and pitch |
| Demo quality | Dashboard and audit view | causal chain visible | live judge flow |

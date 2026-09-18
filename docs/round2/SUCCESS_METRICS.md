# PS-F03 Success Metrics

| Metric | Definition | Capture method |
| --- | --- | --- |
| Settlement latency | `T2 - T0`, where T0 is confirmed trigger condition and T2 is payout completion | Server timestamps in trigger evaluation and payout records |
| Consensus accuracy | Correct consensus/outlier classification divided by labelled synthetic scenarios | Test fixture expected labels vs actual result |
| False-trigger rate | Payout-eligible result when labelled condition is false | Synthetic test-set count / applicable scenarios |
| Missed-trigger rate | No payout-eligible result when labelled condition is true | Synthetic test-set count / applicable scenarios |
| Idempotency success | Duplicate payout attempts that leave one financial effect | Duplicate/retry test cases |

Report trial count, mean and optional p95 only after running trials. Do not fabricate latency or accuracy values.

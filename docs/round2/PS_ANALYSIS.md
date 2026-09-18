# PS-F03 Requirement Analysis

## Requirement to design mapping

| Classification | Requirement or decision | Evidence in prototype |
| --- | --- | --- |
| Official PS requirement | Multi-source telemetry with rejection of corrupted input | Per-source events and validation status in the dashboard and audit log |
| Team design decision | Three synthetic sources, 2-of-3 quorum, median result, 5 mm tolerance | Consensus result with member values and rejected outlier |
| Official PS requirement | Deterministic adjudication against pre-agreed policy | Stored rainfall policy and trigger evaluation record |
| Team design decision | 60-minute rainfall total >= 100 mm; one INR 10,000 synthetic payout | Reproducible fixture and comparison evidence |
| Official PS requirement | Idempotent simulated payout and audit trail | Repeated retry returns the original payout and only one ledger credit |
| Official metric | Trigger-confirmed-to-payout-completed latency | T0, T1, T2 server timestamps and trial summary |

## Recommended consensus algorithm

For a `(region, metric, 60-minute bucket)`, accept schema-valid, fresh, unit-normalized readings from distinct enabled sources. Form the largest group whose readings are within 5 mm of one another. If at least two of the three sources belong to that group, emit the median as the consensus value and mark non-members `SOURCE_DISAGREEMENT`. Otherwise emit `NO_CONSENSUS`; no trigger evaluation can pass. This is a team design decision, not an organizer-mandated number.

It demonstrates a practical Byzantine-fault-inspired property: one source can be anomalous without deciding the result. It is not a claim of formal Byzantine fault tolerance.

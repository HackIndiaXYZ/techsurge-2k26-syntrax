# PS-F03 Test Plan

| Category | Scenario | Expected result |
| --- | --- | --- |
| Normal | 80, 81, 82 mm | quorum achieved, policy `NOT_MET`, no payout |
| Normal | 101, 102, 103 mm | consensus 102 mm, policy `TRIGGERED`, one completed synthetic payout |
| Corruption | 101, 102, 500 mm | outlier retained with rejection reason; two-source consensus is auditable |
| Validation | negative, malformed, stale, future, wrong-unit event | rejected before consensus |
| Consensus | 100, 120, 140 mm | `NO_CONSENSUS`, no payout |
| Availability | one valid source only | `PENDING`, no payout |
| Duplicate | same source/event ID submitted twice | stable duplicate response; one persisted effect |
| Failure | payout transaction rolls back / timeout | `FAILED` or original pending result; no extra credit |
| Retry | repeat execute with same key | original payout response; one transaction |
| Basis risk | labelled loss but 99 mm consensus | `NOT_MET`; document missed-trigger limitation |

Capture expected audit event types for every integration scenario.

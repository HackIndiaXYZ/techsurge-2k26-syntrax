# Audit Trail

The audit trail answers “Why did this payout happen?” by retaining ordered, correlated events with actor, entity reference, UTC time and structured payload. Required event types are `TELEMETRY_RECEIVED`, `TELEMETRY_REJECTED`, `TELEMETRY_DUPLICATED`, `CONSENSUS_STARTED`, `SOURCE_REJECTED`, `CONSENSUS_ACHIEVED`, `CONSENSUS_NOT_ACHIEVED`, `TRIGGER_EVALUATED`, `TRIGGER_FIRED`, `PAYOUT_INITIATED`, `PAYOUT_RETRIED`, `PAYOUT_COMPLETED`, and `PAYOUT_FAILED`.

An evidence view links policy ID/version, all candidate source events and validation reasons, consensus member IDs/value/quorum, trigger threshold/window/comparison, payout ID/key/state, wallet transaction ID/balance change, and T0/T1/T2 timestamps. Application roles do not edit or delete audit records. This is append-only application evidence, not a claim of cryptographic immutability.

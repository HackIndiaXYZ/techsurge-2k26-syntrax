# Canonical PS-F03 Domain Model

This document is the canonical definition for all entities. API payloads, tables, UI fields, AI inputs, tests, and audit records must use these names and semantics.

| Entity | Purpose, key fields, lifecycle |
| --- | --- |
| `Policyholder` | Synthetic owner. `id`, `display_name`, `created_at`; has wallets and policies. No real PII. |
| `MicroRegion` | Named synthetic coverage area. `id`, `code`, `name`, `timezone`, `active`; policies and telemetry reference it. |
| `WeatherSource` | Independent logical source. `id`, `code`, `kind`, `enabled`, `reliability_note`; supplies telemetry. |
| `TelemetryEvent` | Immutable source observation. `id`, `source_event_id`, source/region, metric, value, unit, observed/window/ingested timestamps, metadata, validation state. `RECEIVED -> ACCEPTED|REJECTED|DUPLICATE`. |
| `ValidationResult` | Reasoned outcome attached to a telemetry event. `id`, `event_id`, `rule`, `outcome`, `reason_code`, `evaluated_at`. |
| `ConsensusResult` | One region-metric-window decision. `id`, `region_id`, `metric`, window, `state`, `value`, `unit`, quorum, member count, created_at. `PENDING|ACHIEVED|NO_CONSENSUS|EXPIRED`. |
| `TriggerRule` | Versioned policy condition. `id`, `metric`, `operator`, `threshold_value`, `unit`, `window_minutes`, `version`. |
| `Policy` | Contract-shaped synthetic coverage. `id`, `policyholder_id`, `region_id`, `trigger_rule_id`, `payout_amount_paise`, `currency`, start/end, `status`. `DRAFT|ACTIVE|EXPIRED|TRIGGERED|PAID|CANCELLED`. |
| `TriggerEvaluation` | Deterministic record linking policy and consensus. `id`, `policy_id`, `consensus_result_id`, `outcome`, `reason_code`, `evaluated_at`. |
| `Payout` | One settlement instruction. `id`, `policy_id`, `trigger_evaluation_id`, `wallet_id`, amount, currency, idempotency key, state, timestamps. `PENDING|PROCESSING|COMPLETED|FAILED`. |
| `Wallet` | Synthetic value container. `id`, `policyholder_id`, `currency`, `balance_paise`, `status`; never represents real money. |
| `WalletTransaction` | Immutable ledger effect. `id`, `wallet_id`, `payout_id`, `direction`, `amount_paise`, balance before/after, `occurred_at`; exactly one payout credit. |
| `AuditEvent` | Append-only explanation evidence. `id`, `correlation_id`, entity type/id, event type, actor, structured payload, occurred_at. |

Identifiers are UUIDs generated server-side. Monetary values are integer paise, never floating point. All system timestamps are UTC. A policy has one policyholder, region, trigger rule, and payout amount; a policy can have many evaluations but at most one completed payout.

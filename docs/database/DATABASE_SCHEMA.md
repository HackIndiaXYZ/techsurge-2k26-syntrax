# PostgreSQL Schema Design

## Tables and critical constraints

| Table | Primary columns | Essential constraint or index |
| --- | --- | --- |
| `policyholders` | `id uuid`, `display_name text`, timestamps | unique synthetic display name |
| `micro_regions` | `id`, `code`, `name`, `timezone`, `active` | unique `code` |
| `weather_sources` | `id`, `code`, `kind`, `enabled` | unique `code` |
| `trigger_rules` | `id`, `metric`, `operator`, `threshold_value numeric`, `unit`, `window_minutes`, `version` | unique `(metric, operator, threshold_value, unit, window_minutes, version)` |
| `policies` | foreign keys to holder/region/rule; `payout_amount_paise bigint`; `status`; dates | check `end_at > start_at`; index `(region_id, status, start_at, end_at)` |
| `telemetry_events` | source/region, source event ID, metric/value/unit, observed/window/received timestamps, state, metadata jsonb | unique `(source_id, source_event_id)`; index `(region_id, metric, window_end, validation_state)` |
| `telemetry_validation_results` | `event_id`, rule, outcome, reason code, details jsonb | index `event_id` |
| `consensus_results` | region, metric, window, state, value, quorum | unique `(region_id, metric, window_start, window_end)` |
| `consensus_members` | consensus/event/source, role, normalized value, rejection reason | unique `(consensus_result_id, telemetry_event_id)` |
| `trigger_evaluations` | policy/consensus, outcome, reason, timestamp | unique `(policy_id, consensus_result_id)` |
| `wallets` | policyholder, currency, balance, status | unique `(policyholder_id, currency)` |
| `payouts` | policy/evaluation/wallet, amount, state, key, `initiated_at`, `completed_at` | unique `policy_id`; unique `(idempotency_scope, idempotency_key)` |
| `wallet_transactions` | wallet/payout, direction, amount, before/after balances | unique `payout_id`; check `amount_paise > 0` |
| `audit_events` | correlation, entity, event type, actor, payload, time | index `(correlation_id, occurred_at)` and `(entity_type, entity_id, occurred_at)` |

Use `timestamptz`, `uuid`, `bigint` for paise, `numeric` only for telemetry values, and `jsonb` only for non-canonical source metadata/audit payloads. Foreign keys are restrictive for financial evidence; do not cascade-delete policies, payouts, transactions, or audit events.

## Atomic settlement

In one database transaction: lock the payout row; reject/return it if already completed; insert one wallet transaction with its unique payout ID; update balance; set payout `COMPLETED` and completion time; append audit evidence; commit. A crash rolls the transaction back; a retry reuses the stored idempotency key.

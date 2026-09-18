# Synthetic Parametric Policy Model

The recommended single demo policy is a synthetic rainfall policy, not a real insurance contract. It has a server-generated policy ID, synthetic policyholder and micro-region IDs, a versioned rainfall trigger rule, threshold `100 mm`, window `60 minutes`, payout amount `1,000,000 paise` (displayed as INR 10,000 synthetic), policy start/end timestamps, and lifecycle status.

| Field | Validation reason |
| --- | --- |
| `policy_id` | Immutable identifier for evidence and payout uniqueness |
| `policyholder_id`, `region_id` | Bind coverage and wallet to one synthetic owner/area |
| `trigger_rule_id` | Avoid copying unversioned threshold logic into policy rows |
| `payout_amount_paise`, `currency` | Exact deterministic outcome, stored without float error |
| `starts_at`, `ends_at` | Prevent evaluation before or after coverage |
| `status` | Constrains `DRAFT -> ACTIVE -> TRIGGERED -> PAID` or `EXPIRED/CANCELLED` |

Rainfall is chosen because the organizer’s suggested scenario is a flash flood and the three-number consensus is easy to demonstrate. Temperature, drought and wind are valid future parameter categories but would need separate units, aggregation windows, policy wording and labelled test data.

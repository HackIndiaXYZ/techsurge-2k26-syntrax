# Optional AI Workflow

1. Freeze and test the deterministic path.
2. Train or configure only on synthetic labelled telemetry, if time remains.
3. Run the model offline or asynchronously on persisted records.
4. Display an advisory score/explanation beside, never instead of, rule outcomes.
5. Disable the feature if unavailable; the dashboard continues with audit fields.

Do not put an LLM in a request/retry loop, a transaction, or any action that can create a payout.

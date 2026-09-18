# PS-F03 AI and Agent Rules

An AI component may read approved synthetic telemetry, consensus, policy, audit, and reference data. It may summarize, classify offline test data, or propose a simulation description. It may not create or modify policies, telemetry, consensus results, trigger evaluations, payouts, wallets, transactions, database records, deployment settings, or credentials.

The backend must not call an LLM from the trigger or payout request path. Agent output is advisory, labelled as generated, and has a deterministic fallback: display the stored audit fields directly.

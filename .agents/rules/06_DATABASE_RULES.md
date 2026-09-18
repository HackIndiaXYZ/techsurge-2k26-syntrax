# PS-F03 Database Rules

1. Akshaya owns PostgreSQL/Supabase schema and migrations; all entity names follow `docs/database/DATA_MODEL.md`.
2. Enforce unique source-event, payout-per-policy, idempotency-key and wallet-transaction-per-payout constraints.
3. Use transactions for payout completion and synthetic wallet credit. Persist correlated audit evidence.
4. Store only synthetic policyholder/wallet/payout data in the prototype.

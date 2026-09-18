# Idempotency in Simulated Settlement

Idempotency means that a repeat of the same intended action produces the same safe result, not a second effect. In this MVP: a policy triggers once; a network timeout makes the caller retry; the retry must return the original payout rather than adding another synthetic INR 10,000 credit.

The payout service creates an opaque `idempotency_key` scoped to `PAYOUT_EXECUTE`. PostgreSQL enforces that key and `wallet_transactions.payout_id` as unique. In the same transaction it locks the payout, inserts one credit, updates the synthetic balance, marks the payout complete, and writes audit evidence. Same key + same request returns the stored response. Same key + different request returns `409 IDEMPOTENCY_KEY_REUSED`. A failed transaction has no ledger effect and may be retried with the original key.

Test: execute once, record balance/transaction ID, replay after a simulated timeout, then assert the same payout ID and transaction ID with unchanged post-payout balance.

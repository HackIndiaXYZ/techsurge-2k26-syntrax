# Synthetic Payout Architecture

This is **not a real payment system**. The only supported rail is an internal synthetic wallet ledger used to demonstrate safe settlement mechanics.

```text
trigger evaluation TRIGGERED
  -> create payout instruction (PENDING, idempotency key)
  -> transactionally credit synthetic wallet once
  -> payout COMPLETED or FAILED
  -> append correlated audit events
```

Payout states are `PENDING`, `PROCESSING`, `COMPLETED`, and `FAILED`. A timeout after request submission is ambiguous, so the caller retries with the same idempotency key; it must receive the original completed or in-progress payout instead of another credit. The `wallet_transactions.payout_id` unique constraint simulates exactly-once financial effect even if the caller, service, or network retries.

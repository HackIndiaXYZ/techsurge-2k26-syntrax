# Synthetic Wallet

The synthetic wallet demonstrates a ledger effect only. It has an owner, ISO-style display currency `INR`, integer `balance_paise`, status, timestamps and immutable `WalletTransaction` records. It is not a bank account, stored-value wallet, payment instrument, or usable balance.

Before a clean-trigger scenario, the dashboard shows a seeded synthetic balance. On payout completion, one `CREDIT` transaction carries the payout ID, amount, before/after balance and timestamp. On retry, the same transaction remains the sole credit and the balance does not change. The UI must label balance, currency display and transaction history `SYNTHETIC`.

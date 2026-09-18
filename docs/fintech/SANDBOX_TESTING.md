# Simulated Financial Testing

The PS-F03 prototype has no payment-provider sandbox integration. Tests use seeded synthetic wallets and transaction records in an isolated development database. A successful payout increases `balance_paise` once; retrying uses the same idempotency key and leaves the post-payout balance unchanged.

Do not enter, store, or test real account numbers, UPI IDs, card data, wallet credentials, or payment-provider keys. Public UPI documentation can be cited only as a future fiat-rail reference, not as an active integration.

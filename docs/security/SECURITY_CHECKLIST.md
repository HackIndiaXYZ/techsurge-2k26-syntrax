# Security Checklist

- No real money, account, wallet, customer or provider-contract data.
- No secret in Git, client code, log or screenshot.
- Validate every mutation server-side; set payload and rate limits.
- Enforce source event, payout and transaction unique constraints.
- Use a transaction for wallet credit and payout completion.
- Restrict CORS and protect simulation routes.
- Render audit/source metadata as text, not unsanitized HTML.
- State prototype limits and production gap in demo.

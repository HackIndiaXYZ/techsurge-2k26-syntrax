# Financial System Safety for the Prototype

The most consequential prototype safety property is preventing an extra synthetic wallet credit. Enforce unique source-event IDs, unique payout per policy, unique wallet transaction per payout, stored idempotency keys, transaction boundaries, server-side threshold logic, and audit evidence.

These controls demonstrate a limited simulated settlement workflow. They do not establish PCI compliance, banking security, money-transmission compliance, production wallet custody, or regulatory approval. See [Security](../security/SECURITY.md).

# PS-F03 Tradeoffs

The MVP trades generality for inspectability. A static one-policy, one-region scenario is less flexible than a policy platform, but it makes consensus, threshold logic, and idempotency demonstrable. A 2-of-3 quorum tolerates one outlier but not two colluding or unavailable sources; that limitation must be visible. Polling creates a small delay compared with server push but avoids connection lifecycle complexity. A synthetic ledger proves duplicate protection without misrepresenting a real payment capability.

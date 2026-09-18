# PS-F03 Testing Strategy

Test the causal pipeline rather than isolated screens: fixture telemetry -> persisted validation -> consensus -> policy evaluation -> payout -> one wallet transaction -> audit evidence. Unit-test pure validation, consensus, trigger and idempotency functions; integration-test database constraints and transaction rollback; E2E-test the judge dashboard using seeded scenarios.

Every test asserts both the decision and the non-decision: an invalid event is not a consensus member, no consensus cannot pay, a duplicate is not counted twice, and a retry cannot change a wallet balance twice. Tests run against synthetic data only.

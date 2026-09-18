# PS-F03 MVP Use Cases

1. **Operator runs a normal scenario.** Three valid rainfall readings agree; an active policy is evaluated and remains untriggered if the consensus is below threshold.
2. **Operator runs an outlier scenario.** One source differs materially; the result identifies its rejection and may still form a quorum from the two agreeing readings.
3. **System triggers a policy.** A fresh consensus total reaches 100 mm in the configured 60-minute window, creating one payout instruction and wallet credit.
4. **System receives a duplicate.** A repeated source event is recorded or returned as duplicate, never counted twice.
5. **System retries settlement.** A network-style retry with the same idempotency key returns the original payout and does not change the balance again.
6. **Policyholder or judge reviews evidence.** The policy, input member set, evaluation, transaction, and correlated audit events explain the outcome.

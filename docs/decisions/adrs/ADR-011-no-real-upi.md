# ADR 011 No Real UPI or Payment Rail

## Context

The official PS explicitly disallows real money, accounts and production rails.

## Decision

Use synthetic wallet credits only.

## Alternatives

Production UPI, provider sandbox, stablecoin rail, bank transfer.

## Reason

It complies with the safety boundary while still proving settlement-state correctness.

## Consequences

Documentation calls every payout simulated and lists rail integration as a production gap.

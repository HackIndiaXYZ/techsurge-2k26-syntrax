# ADR 010 No Blockchain

## Context

Oracle and payment language can invite unnecessary blockchain complexity.

## Decision

Use PostgreSQL records, source evidence, and deterministic functions; do not use blockchain.

## Alternatives

Smart contracts, public chain oracle, permissioned ledger.

## Reason

The PS does not require blockchain, and it does not improve the required synthetic flow within the time budget.

## Consequences

Audit integrity is demonstrated with append-only application records, not a tamper-proof ledger claim.

# ADR 001 PostgreSQL

## Context

The prototype needs deduplication, idempotency, relationships, and durable audit joins.

## Decision

Use PostgreSQL, provisioned through Supabase if available.

## Alternatives

In-memory state, document database, or distributed ledger.

## Reason

Unique constraints and transactions directly protect the simulated financial effect and are fast to explain.

## Consequences

The schema and migration work must be coordinated; browser clients do not access the database directly.

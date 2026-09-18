# ADR 005 No LLM Payment Decision

## Context

LLMs can generate plausible language but are non-deterministic and difficult to audit.

## Decision

Do not put an LLM or agent in trigger, consensus, payout or ledger control paths.

## Alternatives

LLM adjudicator or agentic payout workflow.

## Reason

A payment decision needs stable rules, exact evidence, repeatable tests, and bounded authority.

## Consequences

Any optional model is read-only/advisory with a direct audit-data fallback.

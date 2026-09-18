# ADR 004 Deterministic Trigger Engine

## Context

Policy conditions must be pre-agreed and explainable.

## Decision

Evaluate persisted consensus against versioned policy rule fields with pure deterministic logic.

## Alternatives

Manual adjudication, LLM decision, learned classifier.

## Reason

The PS explicitly requires deterministic adjudication and the result must be reproducible.

## Consequences

Rule changes require versioning; policy triggers remain limited to supported parameter types.

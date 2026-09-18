# ADR 012 AI Excluded from MVP Decision Path

## Context

AI may assist with anomaly analysis or explanation, but the team has a 17-hour build constraint.

## Decision

No AI/ML or RAG feature is required for the MVP. If added, it is offline or read-only and advisory.

## Alternatives

Anomaly detector, LLM explainer, RAG assistant, autonomous agent.

## Reason

The deterministic core directly satisfies the PS and is easier to test, demonstrate and trust.

## Consequences

Sanju focuses first on synthetic datasets, labels and architecture review rather than an AI feature.

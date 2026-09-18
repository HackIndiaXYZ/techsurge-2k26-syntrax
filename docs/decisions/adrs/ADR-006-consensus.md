# ADR 006 Three Source Consensus

## Context

The PS requires cross-source validation and resilience to corrupted telemetry.

## Decision

Use three logical sources, 2-of-3 quorum, a 5 mm agreement tolerance, and median of the agreeing group.

## Alternatives

Single source, unanimous source rule, weighted source scores, trimmed mean, blockchain oracle network.

## Reason

It is transparent, testable, handles one outlier, and fits the 17-hour MVP.

## Consequences

Two bad or unavailable sources cause no consensus. This is a prototype policy, not formal Byzantine fault tolerance.

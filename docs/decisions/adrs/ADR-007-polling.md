# ADR 007 Dashboard Polling

## Context

The UI must visibly feel live during a short, controlled demo.

## Decision

Poll the dashboard read model every second during simulation; add SSE only if time remains.

## Alternatives

WebSockets, SSE as default, manual refresh.

## Reason

Polling is simplest to implement, debug, deploy and recover in a low-volume prototype.

## Consequences

Updates can appear up to one poll interval later; the true latency metric remains server-side T2 minus T0.

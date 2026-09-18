# ADR 002 FastAPI

## Context

The backend must expose typed ingestion, read and simulation APIs quickly.

## Decision

Use one FastAPI modular monolith with Pydantic validation and SQLAlchemy.

## Alternatives

Node backend, multiple services, serverless functions.

## Reason

It matches the team baseline and keeps the deterministic core and OpenAPI contract close together.

## Consequences

Long-running provider processing is out of scope; direct request handling is sufficient for seeded volume.

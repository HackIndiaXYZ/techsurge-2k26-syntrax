# ADR 008 Deployment Split

## Context

The team needs a simple deployment option that matches its baseline.

## Decision

Deploy Next.js to Vercel and FastAPI to Render, using Supabase PostgreSQL if approved credentials are available. Railway is a fallback, not a required active deployment.

## Alternatives

One container host, Kubernetes, multi-region cloud architecture.

## Reason

The split is familiar, independently deployable and enough for the demo.

## Consequences

Environment URLs, CORS and secrets need explicit configuration. Local Docker remains a development aid, not a production claim.

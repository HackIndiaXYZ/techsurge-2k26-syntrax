# ADR 009 No Kafka

## Context

The PS calls the pipeline event-driven, but expected MVP event volume is synthetic and small.

## Decision

Use direct API processing and PostgreSQL persistence; do not introduce Kafka, RabbitMQ, Redis, Celery or a queue for the MVP.

## Alternatives

Kafka, RabbitMQ, Celery/Redis, FastAPI background task.

## Reason

The added operations, failure modes and ordering work do not improve the judge-visible core path.

## Consequences

The service is not a high-throughput streaming platform. A queue is a production-scaling consideration.

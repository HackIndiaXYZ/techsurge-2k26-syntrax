# Architecture Decisions

The authoritative records are in [`docs/decisions/adrs/`](../decisions/adrs/). In brief: PostgreSQL provides durable unique constraints and audit joins; FastAPI provides typed contracts and a small direct pipeline; the wallet is synthetic; triggers and payments are deterministic; the consensus layer is a transparent 2-of-3 median; frontend updates poll; and Kafka, blockchain, real UPI, and mandatory AI are deliberately excluded from the MVP.

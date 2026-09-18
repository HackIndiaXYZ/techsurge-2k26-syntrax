# PS-F03 AI Architecture

## Decision boundary

**Deterministic core:** validation rules, consensus membership/value, policy trigger, payout creation, wallet credit, and audit state transitions. These components must never depend on an LLM, agent, RAG answer, confidence score, or learned model.

**Optional AI/ML support:** offline telemetry anomaly scoring, source-quality analysis, synthetic-scenario generation, and plain-language explanations of an already persisted deterministic result. None is required for the MVP.

If implemented after the core is stable, a small anomaly model receives normalized telemetry features (value, deviation from peer median, age, source ID encoding, prior quality label) and returns `anomaly_score` plus feature explanation. The score appears as advisory evidence and never rejects, accepts, triggers, or pays by itself; deterministic validation and consensus remain the fallback.

# SYNTRAX AI/ML Advisory Layer

A **modular, advisory-only** AI layer for the PS-F03 Autonomous Parametric Climate Insurance Engine.

## Architecture Boundary

```
DETERMINISTIC CORE (Ramraj):
  telemetry → validation → consensus → trigger → payout → wallet → audit

AI LAYER (Sanju — this module):
  Read-only advisory intelligence. Never authoritative.
  Can be disabled without affecting core.
```

## Modules

| Module | Purpose | LLM Required? |
|--------|---------|---------------|
| `anomaly` | Statistical telemetry anomaly detection | No — pure statistics |
| `explainer` | Human-readable event explanations | No — template-based |
| `localizer` | Local-language message generation | No — structured templates |
| `schemas` | Shared Pydantic input/output contracts | No |
| `fixtures` | Scenario test data for all demo scenarios | No |

## Key Principle

> **AI NEVER:** approves payouts, rejects payouts, modifies thresholds, modifies amounts, transfers money, or overrides deterministic policy rules.

> **AI MAY:** score anomalies (advisory), explain events (read-only), generate notifications (post-settlement), provide policy explanation (informational).

## Running

```bash
cd ai
pip install -r requirements.txt
pytest tests/ -v
```

## Integration with Backend

The AI layer exposes pure Python functions that the backend can optionally call. If the AI module is unavailable or raises an exception, the backend continues unaffected with deterministic fallback values.

```python
from ai.anomaly import score_telemetry_anomaly
from ai.explainer import explain_event
from ai.localizer import generate_settlement_message
```

All functions accept structured data (Pydantic models) and return structured results with explicit confidence scores and fallback indicators.


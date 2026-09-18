# PROBLEM STATEMENT — PS-F03

**Status:** ACTIVE (Round 2 live problem — revealed at TechSurge 2K26 / Kalachakra)
**Updated by:** Ramraj (backend/ramraj) — 2026-09-18

---

## PS-F03 | Autonomous Parametric Climate Insurance & Instant Settlement Engine

### Problem

Traditional crop/climate insurance relies on manual claims, field assessments, and slow
bureaucratic settlement processes. Farmers in climate-risk zones (e.g., flood-prone river
deltas) suffer long delays between a weather event and receiving any financial relief.

### Required Solution (Prototype)

Build an autonomous, rules-based parametric insurance engine that:

1. Ingests simulated multi-source weather telemetry (rainfall)
2. Validates and deduplicates observations
3. Establishes authoritative consensus across multiple sources
4. Evaluates a predefined parametric trigger rule deterministically
5. Executes an instant simulated payout to a synthetic wallet — if and only if the trigger fires
6. Records a complete, traceable audit trail of every state transition

### Prototype Constraints

- **No real money** — synthetic ledger only
- **No real bank account or wallet**
- **No real UPI**
- **No production payment gateway**
- **No blockchain**
- **No production weather-provider contracts**
- **No production financial claims**

### Frozen Demo Parameters

| Parameter | Value |
|---|---|
| Weather metric | Rainfall (mm) |
| Trigger threshold | ≥ 100 mm |
| Observation window | 60 minutes |
| Simulated sources | 3 (A, B, C) |
| Consensus quorum | 2 of 3 minimum |
| Consensus method | Median |
| Tolerance | ≤ 5 mm (inclusive) |
| Demo payout | ₹10,000 = 1,000,000 paise |
| Money representation | Integer paise (never float) |
| Micro-region | Kaveri Delta (demo seed) |

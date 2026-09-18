"""
SYNTRAX AI Layer — Scenario Fixture Data

Complete fixture data for all demo scenarios. Each fixture defines:
  - Input telemetry readings
  - Expected validation outcomes
  - Expected consensus result
  - Expected trigger evaluation
  - Expected payout behavior
  - Expected audit events

These fixtures are the single source of truth for:
  1. Backend integration tests (Ramraj + Akshaya)
  2. Frontend mock data (Nikhil)
  3. AI module tests (Sanju)
  4. Demo rehearsal (all)

All data uses SYN- prefixes. No real people, locations, or financial data.
"""

from __future__ import annotations

from datetime import datetime, timezone

# ============================================================
# Reference IDs (deterministic for testing)
# ============================================================

# These would be UUIDs in the real system. Using readable strings
# for fixture clarity. The backend seed script maps these to UUIDs.
REGION_ID = "SYN-REGION-001"
REGION_NAME = "Kurnool Synthetic Micro-Region"

HOLDER_ID = "SYN-HOLDER-001"
HOLDER_NAME = "Ravi Kumar (Synthetic Farmer)"

WALLET_ID = "SYN-WALLET-001"
WALLET_INITIAL_BALANCE_PAISE = 500_000  # ₹5,000

POLICY_ID = "SYN-POLICY-RAIN-001"
POLICY_AMOUNT_PAISE = 1_000_000  # ₹10,000
POLICY_CURRENCY = "INR"

SOURCE_A_ID = "SYN-SRC-A"
SOURCE_B_ID = "SYN-SRC-B"
SOURCE_C_ID = "SYN-SRC-C"

TRIGGER_THRESHOLD = 100.0  # mm
TRIGGER_OPERATOR = "GTE"
TRIGGER_WINDOW_MINUTES = 60
TRIGGER_METRIC = "RAINFALL_MM"
TRIGGER_UNIT = "mm"

# Fixed window for demo consistency
DEMO_WINDOW_START = datetime(2026, 9, 18, 9, 0, 0, tzinfo=timezone.utc)
DEMO_WINDOW_END = datetime(2026, 9, 18, 10, 0, 0, tzinfo=timezone.utc)
DEMO_OBSERVED_AT = datetime(2026, 9, 18, 10, 0, 0, tzinfo=timezone.utc)


# ============================================================
# Scenario 1: Clean Trigger
# ============================================================
# All 3 sources agree. Consensus achieved. Policy triggers. Payout completes.
SCENARIO_CLEAN_TRIGGER = {
    "name": "clean-trigger",
    "description": "All sources agree, consensus achieved, policy triggers, payout completes.",
    "readings": [
        {
            "source_code": SOURCE_A_ID,
            "source_event_id": "clean-src-a-001",
            "value": 101.0,
            "unit": "mm",
            "metadata": {"scenario": "clean-trigger"},
        },
        {
            "source_code": SOURCE_B_ID,
            "source_event_id": "clean-src-b-001",
            "value": 102.0,
            "unit": "mm",
            "metadata": {"scenario": "clean-trigger"},
        },
        {
            "source_code": SOURCE_C_ID,
            "source_event_id": "clean-src-c-001",
            "value": 103.0,
            "unit": "mm",
            "metadata": {"scenario": "clean-trigger"},
        },
    ],
    "expected": {
        "validation": {
            SOURCE_A_ID: "ACCEPTED",
            SOURCE_B_ID: "ACCEPTED",
            SOURCE_C_ID: "ACCEPTED",
        },
        "consensus": {
            "state": "ACHIEVED",
            "value": 102.0,  # Median of [101, 102, 103]
            "member_count": 3,
            "quorum_met": True,
        },
        "trigger": {
            "outcome": "TRIGGERED",
            "reason_code": "THRESHOLD_MET",
            # 102.0 >= 100.0
        },
        "payout": {
            "state": "COMPLETED",
            "amount_paise": POLICY_AMOUNT_PAISE,
        },
        "wallet": {
            "balance_before_paise": WALLET_INITIAL_BALANCE_PAISE,
            "balance_after_paise": WALLET_INITIAL_BALANCE_PAISE + POLICY_AMOUNT_PAISE,
        },
        "audit_events": [
            "TELEMETRY_RECEIVED",  # x3
            "CONSENSUS_ACHIEVED",
            "TRIGGER_FIRED",
            "PAYOUT_INITIATED",
            "PAYOUT_COMPLETED",
            "WALLET_CREDITED",
        ],
    },
}


# ============================================================
# Scenario 2: Corrupted Source
# ============================================================
# Source C reports 500mm (outlier). A+B agree. Consensus from 2 sources.
SCENARIO_CORRUPTED_SOURCE = {
    "name": "corrupted-source",
    "description": "One corrupted source (500mm). Two valid sources form consensus.",
    "readings": [
        {
            "source_code": SOURCE_A_ID,
            "source_event_id": "corrupt-src-a-001",
            "value": 101.0,
            "unit": "mm",
            "metadata": {"scenario": "corrupted-source"},
        },
        {
            "source_code": SOURCE_B_ID,
            "source_event_id": "corrupt-src-b-001",
            "value": 102.0,
            "unit": "mm",
            "metadata": {"scenario": "corrupted-source"},
        },
        {
            "source_code": SOURCE_C_ID,
            "source_event_id": "corrupt-src-c-001",
            "value": 500.0,
            "unit": "mm",
            "metadata": {"scenario": "corrupted-source", "note": "simulated corrupted reading"},
        },
    ],
    "expected": {
        "validation": {
            # Note: 500mm is ABOVE the 400mm range limit, so it's REJECTED
            # by deterministic validation, not just consensus outlier.
            # If we want it to pass validation but fail consensus,
            # use a value like 350mm instead.
            SOURCE_A_ID: "ACCEPTED",
            SOURCE_B_ID: "ACCEPTED",
            SOURCE_C_ID: "REJECTED",  # >400mm impossible value
        },
        "consensus": {
            "state": "ACHIEVED",
            "value": 101.5,  # Median of [101, 102]
            "member_count": 2,
            "quorum_met": True,
        },
        "trigger": {
            "outcome": "TRIGGERED",
            "reason_code": "THRESHOLD_MET",
            # 101.5 >= 100.0
        },
        "payout": {
            "state": "COMPLETED",
            "amount_paise": POLICY_AMOUNT_PAISE,
        },
    },
}


# ============================================================
# Scenario 2b: Corrupted Source (Consensus Outlier, not Validation Reject)
# ============================================================
# Source C reports 350mm (within range but disagrees with A+B).
SCENARIO_CORRUPTED_SOURCE_OUTLIER = {
    "name": "corrupted-source-outlier",
    "description": "One source is within valid range but disagrees with peers (consensus outlier).",
    "readings": [
        {
            "source_code": SOURCE_A_ID,
            "source_event_id": "outlier-src-a-001",
            "value": 101.0,
            "unit": "mm",
            "metadata": {"scenario": "corrupted-source-outlier"},
        },
        {
            "source_code": SOURCE_B_ID,
            "source_event_id": "outlier-src-b-001",
            "value": 102.0,
            "unit": "mm",
            "metadata": {"scenario": "corrupted-source-outlier"},
        },
        {
            "source_code": SOURCE_C_ID,
            "source_event_id": "outlier-src-c-001",
            "value": 350.0,
            "unit": "mm",
            "metadata": {"scenario": "corrupted-source-outlier", "note": "valid range but outlier"},
        },
    ],
    "expected": {
        "validation": {
            SOURCE_A_ID: "ACCEPTED",
            SOURCE_B_ID: "ACCEPTED",
            SOURCE_C_ID: "ACCEPTED",  # Passes range check (<400)
        },
        "consensus": {
            "state": "ACHIEVED",
            "value": 101.5,  # Median of [101, 102]; C is outlier (|350-101| >> 5mm)
            "member_count": 2,
            "quorum_met": True,
            "outlier": SOURCE_C_ID,
        },
        "trigger": {
            "outcome": "TRIGGERED",
            "reason_code": "THRESHOLD_MET",
        },
    },
}


# ============================================================
# Scenario 3: No Consensus
# ============================================================
# All sources wildly disagree. No group of 2 within 5mm.
SCENARIO_NO_CONSENSUS = {
    "name": "no-consensus",
    "description": "All sources disagree. No consensus. No payout.",
    "readings": [
        {
            "source_code": SOURCE_A_ID,
            "source_event_id": "nocon-src-a-001",
            "value": 50.0,
            "unit": "mm",
            "metadata": {"scenario": "no-consensus"},
        },
        {
            "source_code": SOURCE_B_ID,
            "source_event_id": "nocon-src-b-001",
            "value": 150.0,
            "unit": "mm",
            "metadata": {"scenario": "no-consensus"},
        },
        {
            "source_code": SOURCE_C_ID,
            "source_event_id": "nocon-src-c-001",
            "value": 250.0,
            "unit": "mm",
            "metadata": {"scenario": "no-consensus"},
        },
    ],
    "expected": {
        "validation": {
            SOURCE_A_ID: "ACCEPTED",
            SOURCE_B_ID: "ACCEPTED",
            SOURCE_C_ID: "ACCEPTED",
        },
        "consensus": {
            "state": "NO_CONSENSUS",
            "value": None,
            "member_count": 0,
            "quorum_met": False,
        },
        "trigger": {
            "outcome": "NO_CONSENSUS",
            "reason_code": "CONSENSUS_NOT_ACHIEVED",
        },
        "payout": None,  # No payout created
    },
}


# ============================================================
# Scenario 4: Duplicate Event
# ============================================================
# Same (source_id, source_event_id) sent twice. Second is DUPLICATE.
SCENARIO_DUPLICATE_EVENT = {
    "name": "duplicate-event",
    "description": "Duplicate source event ID. Second submission returns original result.",
    "readings": [
        {
            "source_code": SOURCE_A_ID,
            "source_event_id": "dup-src-a-001",
            "value": 101.0,
            "unit": "mm",
            "metadata": {"scenario": "duplicate-event", "attempt": 1},
        },
    ],
    "duplicate_reading": {
        "source_code": SOURCE_A_ID,
        "source_event_id": "dup-src-a-001",  # Same event ID!
        "value": 101.0,
        "unit": "mm",
        "metadata": {"scenario": "duplicate-event", "attempt": 2},
    },
    "expected": {
        "first_response": {
            "status_code": 202,
            "validation_state": "ACCEPTED",
        },
        "second_response": {
            "status_code": 200,
            "validation_state": "DUPLICATE",
        },
    },
}


# ============================================================
# Scenario 5: Missing Source
# ============================================================
# Only 2 of 3 sources report. Consensus still possible with 2-of-3 quorum.
SCENARIO_MISSING_SOURCE = {
    "name": "missing-source",
    "description": "Only 2 sources report. Consensus formed from available data.",
    "readings": [
        {
            "source_code": SOURCE_A_ID,
            "source_event_id": "miss-src-a-001",
            "value": 105.0,
            "unit": "mm",
            "metadata": {"scenario": "missing-source"},
        },
        {
            "source_code": SOURCE_B_ID,
            "source_event_id": "miss-src-b-001",
            "value": 108.0,
            "unit": "mm",
            "metadata": {"scenario": "missing-source"},
        },
        # Source C is missing — not submitted
    ],
    "expected": {
        "validation": {
            SOURCE_A_ID: "ACCEPTED",
            SOURCE_B_ID: "ACCEPTED",
        },
        "consensus": {
            "state": "ACHIEVED",
            "value": 106.5,  # Median of [105, 108]
            "member_count": 2,
            "quorum_met": True,
        },
        "trigger": {
            "outcome": "TRIGGERED",
            "reason_code": "THRESHOLD_MET",
        },
    },
}


# ============================================================
# Scenario 6: Payout Retry (Idempotency)
# ============================================================
# After a successful payout, retry the execute call. Same result, no double credit.
SCENARIO_PAYOUT_RETRY = {
    "name": "payout-retry",
    "description": "Payout execute retry with same idempotency key. No double credit.",
    "prerequisite": "Run clean-trigger scenario first.",
    "expected": {
        "first_execute": {
            "status_code": 201,
            "payout_state": "COMPLETED",
            "transaction_count": 1,
        },
        "retry_execute": {
            "status_code": 200,
            "payout_state": "COMPLETED",
            "transaction_count": 1,  # Still 1, not 2
            "same_payout_id": True,
            "same_transaction_id": True,
            "balance_unchanged": True,
        },
    },
}


# ============================================================
# Scenario 7: Below Threshold
# ============================================================
# All sources agree but below the 100mm trigger threshold.
SCENARIO_BELOW_THRESHOLD = {
    "name": "below-threshold",
    "description": "Consensus achieved but below trigger threshold. No payout.",
    "readings": [
        {
            "source_code": SOURCE_A_ID,
            "source_event_id": "below-src-a-001",
            "value": 45.0,
            "unit": "mm",
            "metadata": {"scenario": "below-threshold"},
        },
        {
            "source_code": SOURCE_B_ID,
            "source_event_id": "below-src-b-001",
            "value": 47.0,
            "unit": "mm",
            "metadata": {"scenario": "below-threshold"},
        },
        {
            "source_code": SOURCE_C_ID,
            "source_event_id": "below-src-c-001",
            "value": 48.0,
            "unit": "mm",
            "metadata": {"scenario": "below-threshold"},
        },
    ],
    "expected": {
        "consensus": {
            "state": "ACHIEVED",
            "value": 47.0,  # Median of [45, 47, 48]
            "member_count": 3,
        },
        "trigger": {
            "outcome": "NOT_MET",
            "reason_code": "BELOW_THRESHOLD",
            # 47.0 < 100.0
        },
        "payout": None,
    },
}


# ============================================================
# Scenario 8: Extreme Invalid Value
# ============================================================
# Source sends a negative value (impossible for rainfall).
SCENARIO_EXTREME_INVALID = {
    "name": "extreme-invalid",
    "description": "Source sends impossible value (-50mm). Rejected by validation.",
    "readings": [
        {
            "source_code": SOURCE_A_ID,
            "source_event_id": "invalid-src-a-001",
            "value": -50.0,
            "unit": "mm",
            "metadata": {"scenario": "extreme-invalid"},
        },
    ],
    "expected": {
        "validation": {
            SOURCE_A_ID: "REJECTED",
        },
        "rejection_reason": "IMPOSSIBLE_VALUE",
    },
}


# ============================================================
# Scenario 9: Barely Crossed Threshold
# ============================================================
# Consensus exactly at threshold. Tests >= comparison.
SCENARIO_BARELY_CROSSED = {
    "name": "barely-crossed",
    "description": "Consensus exactly at 100mm threshold. GTE operator triggers.",
    "readings": [
        {
            "source_code": SOURCE_A_ID,
            "source_event_id": "barely-src-a-001",
            "value": 99.0,
            "unit": "mm",
            "metadata": {"scenario": "barely-crossed"},
        },
        {
            "source_code": SOURCE_B_ID,
            "source_event_id": "barely-src-b-001",
            "value": 100.0,
            "unit": "mm",
            "metadata": {"scenario": "barely-crossed"},
        },
        {
            "source_code": SOURCE_C_ID,
            "source_event_id": "barely-src-c-001",
            "value": 101.0,
            "unit": "mm",
            "metadata": {"scenario": "barely-crossed"},
        },
    ],
    "expected": {
        "consensus": {
            "state": "ACHIEVED",
            "value": 100.0,  # Median of [99, 100, 101]
            "member_count": 3,
        },
        "trigger": {
            "outcome": "TRIGGERED",
            "reason_code": "THRESHOLD_MET",
            # 100.0 >= 100.0 (GTE)
        },
    },
}


# ============================================================
# All Scenarios (for iteration)
# ============================================================

ALL_SCENARIOS = [
    SCENARIO_CLEAN_TRIGGER,
    SCENARIO_CORRUPTED_SOURCE,
    SCENARIO_CORRUPTED_SOURCE_OUTLIER,
    SCENARIO_NO_CONSENSUS,
    SCENARIO_DUPLICATE_EVENT,
    SCENARIO_MISSING_SOURCE,
    SCENARIO_PAYOUT_RETRY,
    SCENARIO_BELOW_THRESHOLD,
    SCENARIO_EXTREME_INVALID,
    SCENARIO_BARELY_CROSSED,
]


def get_scenario(name: str) -> dict | None:
    """Look up a scenario fixture by name."""
    for scenario in ALL_SCENARIOS:
        if scenario["name"] == name:
            return scenario
    return None


def list_scenario_names() -> list[str]:
    """Return all available scenario names."""
    return [s["name"] for s in ALL_SCENARIOS]


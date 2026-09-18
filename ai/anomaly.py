"""
SYNTRAX AI Layer — Telemetry Anomaly Detection

ADVISORY ONLY. This module identifies statistically unusual weather
observations. It uses pure statistics (z-score, median absolute deviation)
— no LLM, no neural network, no external API.

CRITICAL BOUNDARY:
  - This module NEVER rejects or accepts telemetry.
  - This module NEVER participates in consensus.
  - This module NEVER triggers or approves payouts.
  - The deterministic validation pipeline is authoritative.
  - If this module fails, the core pipeline continues unaffected.

Algorithm: Modified Z-Score using Median Absolute Deviation (MAD)
  - Robust to outliers (unlike mean/stdev)
  - Works with as few as 3 data points
  - Deterministic — same inputs always produce same outputs

Thresholds (team design decisions, not scientific claims):
  - |z| < 2.0  → NORMAL
  - 2.0 ≤ |z| < 3.5 → SUSPICIOUS
  - |z| ≥ 3.5  → ANOMALOUS
"""

from __future__ import annotations

import logging
import statistics
from typing import Optional

from .schemas import (
    AnomalyInput,
    AnomalyLevel,
    AnomalyOutput,
    AnomalyScore,
)

logger = logging.getLogger(__name__)

# Thresholds for anomaly classification (team design decisions)
_SUSPICIOUS_THRESHOLD = 2.0
_ANOMALOUS_THRESHOLD = 3.5

# Constant for MAD-to-standard-deviation scaling (assumes normality)
# See: https://en.wikipedia.org/wiki/Median_absolute_deviation
_MAD_SCALE = 1.4826


def score_telemetry_anomaly(input_data: AnomalyInput) -> AnomalyOutput:
    """Score each telemetry reading for anomaly likelihood.

    Args:
        input_data: All readings for a single consensus window.

    Returns:
        AnomalyOutput with per-source anomaly scores.
        Always succeeds — returns fallback scores on any internal error.

    This function is ADVISORY. Its output must never be used to
    accept/reject telemetry, compute consensus, or trigger payouts.
    """
    try:
        return _compute_anomaly_scores(input_data)
    except Exception as exc:
        logger.warning(
            "Anomaly detection failed (advisory only, continuing): %s", exc,
            exc_info=True,
        )
        return _fallback_output(input_data)


def _compute_anomaly_scores(input_data: AnomalyInput) -> AnomalyOutput:
    """Core anomaly scoring logic using Modified Z-Score (MAD)."""

    # Extract valid readings (only ACCEPTED telemetry participates)
    valid_readings = [r for r in input_data.readings if r.validation_state == "ACCEPTED"]

    if not valid_readings:
        return _fallback_output(input_data)

    values = [r.value for r in valid_readings]
    n = len(values)

    # Compute peer statistics
    peer_median = statistics.median(values)
    peer_spread = max(values) - min(values) if n > 1 else 0.0

    # Compute MAD-based z-scores
    mad = _compute_mad(values)
    z_scores = _compute_z_scores(values, peer_median, mad)

    # Score each reading
    source_scores: list[AnomalyScore] = []

    for i, reading in enumerate(valid_readings):
        deviation = abs(reading.value - peer_median)
        z = z_scores[i] if z_scores else None
        level = _classify_anomaly(z, deviation, peer_spread, n)

        explanation = _generate_explanation(
            reading.source_code,
            reading.value,
            peer_median,
            deviation,
            z,
            level,
            input_data.metric,
        )

        source_scores.append(AnomalyScore(
            source_code=reading.source_code,
            value=reading.value,
            anomaly_score=_z_to_score(z, deviation, peer_spread),
            anomaly_level=level,
            deviation_from_median=round(deviation, 2),
            z_score=round(z, 4) if z is not None else None,
            explanation=explanation,
        ))

    # Also include rejected/duplicate readings with explicit labeling
    for reading in input_data.readings:
        if reading.validation_state != "ACCEPTED":
            source_scores.append(AnomalyScore(
                source_code=reading.source_code,
                value=reading.value,
                anomaly_score=1.0,  # Validation-rejected is max anomaly
                anomaly_level=AnomalyLevel.ANOMALOUS,
                deviation_from_median=abs(reading.value - peer_median) if peer_median else 0.0,
                z_score=None,
                explanation=(
                    f"Source {reading.source_code} reported {reading.value}{input_data.readings[0].unit} "
                    f"but was {reading.validation_state} by deterministic validation. "
                    f"This AI score is advisory and did not influence that decision."
                ),
            ))

    return AnomalyOutput(
        region_id=input_data.region_id,
        metric=input_data.metric,
        window_start=input_data.window_start,
        window_end=input_data.window_end,
        source_scores=source_scores,
        peer_median=round(peer_median, 2),
        peer_spread=round(peer_spread, 2),
        reading_count=n,
        is_advisory=True,
        method="statistical_mad_zscore",
        fallback_used=False,
    )


def _compute_mad(values: list[float]) -> float:
    """Compute Median Absolute Deviation.

    MAD = median(|xi - median(x)|)

    More robust than standard deviation for small samples with outliers.
    """
    if len(values) < 2:
        return 0.0
    med = statistics.median(values)
    absolute_deviations = [abs(v - med) for v in values]
    return statistics.median(absolute_deviations)


def _compute_z_scores(
    values: list[float],
    median: float,
    mad: float,
) -> Optional[list[float]]:
    """Compute Modified Z-Scores using MAD.

    Modified Z-Score = 0.6745 * (xi - median) / MAD

    The 0.6745 factor makes the score comparable to standard z-scores
    under normality assumption. We use the equivalent MAD_SCALE = 1.4826
    applied to MAD to get a robust standard deviation estimate.

    Returns None if MAD is zero (all values identical).
    """
    if mad == 0.0:
        return None  # All values identical; no meaningful z-score

    # Robust estimate of standard deviation
    robust_std = mad * _MAD_SCALE

    return [(v - median) / robust_std for v in values]


def _classify_anomaly(
    z_score: Optional[float],
    deviation: float,
    spread: float,
    n: int,
) -> AnomalyLevel:
    """Classify anomaly level from z-score.

    Falls back to deviation-based heuristic if z-score unavailable.
    """
    if z_score is not None:
        abs_z = abs(z_score)
        if abs_z >= _ANOMALOUS_THRESHOLD:
            return AnomalyLevel.ANOMALOUS
        if abs_z >= _SUSPICIOUS_THRESHOLD:
            return AnomalyLevel.SUSPICIOUS
        return AnomalyLevel.NORMAL

    # Fallback: deviation-based when all values are identical or n < 3
    if n < 2:
        return AnomalyLevel.NORMAL
    if deviation == 0.0:
        return AnomalyLevel.NORMAL

    # Use team consensus tolerance (5mm) as reference
    if deviation > 50.0:  # >10x the consensus tolerance
        return AnomalyLevel.ANOMALOUS
    if deviation > 20.0:  # >4x the consensus tolerance
        return AnomalyLevel.SUSPICIOUS
    return AnomalyLevel.NORMAL


def _z_to_score(
    z_score: Optional[float],
    deviation: float,
    spread: float,
) -> float:
    """Convert z-score to a 0-1 anomaly score.

    Uses a sigmoid-like mapping: score = min(1.0, |z| / (2 * threshold))
    """
    if z_score is not None:
        abs_z = abs(z_score)
        # Map: z=0 → 0.0, z=3.5 → 0.8, z≥7 → 1.0
        score = min(1.0, abs_z / (2 * _ANOMALOUS_THRESHOLD))
        return round(score, 4)

    # Fallback: deviation-based
    if spread == 0.0:
        return 0.0
    score = min(1.0, deviation / max(spread, 1.0))
    return round(score, 4)


def _generate_explanation(
    source_code: str,
    value: float,
    median: float,
    deviation: float,
    z_score: Optional[float],
    level: AnomalyLevel,
    metric: str,
) -> str:
    """Generate a deterministic human-readable explanation.

    Template-based. No LLM. Same inputs always produce same outputs.
    """
    unit = "mm" if "RAINFALL" in metric else ""

    if level == AnomalyLevel.NORMAL:
        return (
            f"Source {source_code} reported {value}{unit}, which is within "
            f"normal range (median: {median}{unit}, deviation: {deviation}{unit})."
        )

    if level == AnomalyLevel.SUSPICIOUS:
        z_info = f", z-score: {z_score:.2f}" if z_score is not None else ""
        return (
            f"Source {source_code} reported {value}{unit}, which deviates "
            f"noticeably from the peer median of {median}{unit} "
            f"(deviation: {deviation}{unit}{z_info}). "
            f"This advisory flag does not affect the deterministic consensus."
        )

    # ANOMALOUS
    z_info = f", z-score: {z_score:.2f}" if z_score is not None else ""
    return (
        f"Source {source_code} reported {value}{unit}, which is a significant "
        f"outlier compared to the peer median of {median}{unit} "
        f"(deviation: {deviation}{unit}{z_info}). "
        f"This advisory flag does not reject the reading or alter consensus. "
        f"The deterministic validation pipeline is authoritative."
    )


def _fallback_output(input_data: AnomalyInput) -> AnomalyOutput:
    """Generate a safe fallback when anomaly detection cannot run.

    All readings scored as NORMAL with a fallback indicator.
    """
    source_scores = [
        AnomalyScore(
            source_code=r.source_code,
            value=r.value,
            anomaly_score=0.0,
            anomaly_level=AnomalyLevel.NORMAL,
            deviation_from_median=0.0,
            z_score=None,
            explanation=(
                f"Anomaly detection unavailable for {r.source_code}. "
                f"Deterministic validation is unaffected."
            ),
        )
        for r in input_data.readings
    ]

    return AnomalyOutput(
        region_id=input_data.region_id,
        metric=input_data.metric,
        window_start=input_data.window_start,
        window_end=input_data.window_end,
        source_scores=source_scores,
        peer_median=0.0,
        peer_spread=0.0,
        reading_count=len(input_data.readings),
        is_advisory=True,
        method="fallback",
        fallback_used=True,
    )


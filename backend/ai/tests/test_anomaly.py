import pytest
from datetime import datetime, timezone

from ai.anomaly import score_telemetry_anomaly
from ai.schemas import AnomalyInput, TelemetryReading, AnomalyLevel

def test_anomaly_clean_trigger():
    # Construct a clean input where all readings are close
    input_data = AnomalyInput(
        region_id="SYN-REGION-001",
        metric="RAINFALL_MM",
        window_start=datetime(2026, 9, 18, 9, 0, 0, tzinfo=timezone.utc),
        window_end=datetime(2026, 9, 18, 10, 0, 0, tzinfo=timezone.utc),
        readings=[
            TelemetryReading(
                source_id="id1", source_code="SYN-SRC-A", value=101.0, 
                observed_at=datetime(2026, 9, 18, 10, 0, 0, tzinfo=timezone.utc), validation_state="ACCEPTED"
            ),
            TelemetryReading(
                source_id="id2", source_code="SYN-SRC-B", value=102.0, 
                observed_at=datetime(2026, 9, 18, 10, 0, 0, tzinfo=timezone.utc), validation_state="ACCEPTED"
            ),
            TelemetryReading(
                source_id="id3", source_code="SYN-SRC-C", value=103.0, 
                observed_at=datetime(2026, 9, 18, 10, 0, 0, tzinfo=timezone.utc), validation_state="ACCEPTED"
            ),
        ]
    )
    
    result = score_telemetry_anomaly(input_data)
    
    assert result.is_advisory is True
    assert result.peer_median == 102.0
    assert result.peer_spread == 2.0
    
    # All should be normal
    for score in result.source_scores:
        assert score.anomaly_level == AnomalyLevel.NORMAL
        assert score.anomaly_score < 1.0


def test_anomaly_corrupted_source():
    # Construct an input with an outlier
    input_data = AnomalyInput(
        region_id="SYN-REGION-001",
        metric="RAINFALL_MM",
        window_start=datetime(2026, 9, 18, 9, 0, 0, tzinfo=timezone.utc),
        window_end=datetime(2026, 9, 18, 10, 0, 0, tzinfo=timezone.utc),
        readings=[
            TelemetryReading(
                source_id="id1", source_code="SYN-SRC-A", value=101.0, 
                observed_at=datetime(2026, 9, 18, 10, 0, 0, tzinfo=timezone.utc), validation_state="ACCEPTED"
            ),
            TelemetryReading(
                source_id="id2", source_code="SYN-SRC-B", value=102.0, 
                observed_at=datetime(2026, 9, 18, 10, 0, 0, tzinfo=timezone.utc), validation_state="ACCEPTED"
            ),
            TelemetryReading(
                source_id="id3", source_code="SYN-SRC-C", value=500.0, 
                observed_at=datetime(2026, 9, 18, 10, 0, 0, tzinfo=timezone.utc), validation_state="ACCEPTED"
            ),
        ]
    )
    
    result = score_telemetry_anomaly(input_data)
    
    # Find the corrupted source
    corrupted_score = next(s for s in result.source_scores if s.source_code == "SYN-SRC-C")
    assert corrupted_score.anomaly_level == AnomalyLevel.ANOMALOUS
    assert corrupted_score.anomaly_score > 0.0

def test_anomaly_rejected_source():
    # Construct an input where a source is pre-rejected by validation
    input_data = AnomalyInput(
        region_id="SYN-REGION-001",
        metric="RAINFALL_MM",
        window_start=datetime(2026, 9, 18, 9, 0, 0, tzinfo=timezone.utc),
        window_end=datetime(2026, 9, 18, 10, 0, 0, tzinfo=timezone.utc),
        readings=[
            TelemetryReading(
                source_id="id1", source_code="SYN-SRC-A", value=101.0, 
                observed_at=datetime(2026, 9, 18, 10, 0, 0, tzinfo=timezone.utc), validation_state="ACCEPTED"
            ),
            TelemetryReading(
                source_id="id3", source_code="SYN-SRC-C", value=-50.0, 
                observed_at=datetime(2026, 9, 18, 10, 0, 0, tzinfo=timezone.utc), validation_state="REJECTED"
            ),
        ]
    )
    
    result = score_telemetry_anomaly(input_data)
    
    rejected_score = next(s for s in result.source_scores if s.source_code == "SYN-SRC-C")
    assert rejected_score.anomaly_level == AnomalyLevel.ANOMALOUS
    assert rejected_score.anomaly_score == 1.0
    assert "REJECTED" in rejected_score.explanation

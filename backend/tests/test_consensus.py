import math
from datetime import datetime, timezone, timedelta
from services.consensus import evaluate_consensus, SourceObservation, ConsensusStatus

def make_obs(source_id: str, value: float, age_seconds: float = 0) -> SourceObservation:
    now = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    return SourceObservation(
        source_id=source_id,
        value_mm=value,
        observed_at=now - timedelta(seconds=age_seconds)
    )

def test_case1_normal():
    obs = [make_obs("A", 110), make_obs("B", 108), make_obs("C", 111)]
    out = evaluate_consensus(obs, evaluated_at=datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc))
    assert out.status == ConsensusStatus.REACHED
    assert len(out.accepted_sources) == 3
    assert out.consensus_value_mm == 110.0

def test_case2_corrupted():
    obs = [make_obs("A", 110), make_obs("B", 108), make_obs("C", 7)]
    out = evaluate_consensus(obs, evaluated_at=datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc))
    assert out.status == ConsensusStatus.REACHED
    assert len(out.accepted_sources) == 2
    assert "C" in out.outlier_sources
    assert out.consensus_value_mm == 109.0

def test_case3_no_consensus():
    obs = [make_obs("A", 120), make_obs("B", 50), make_obs("C", 5)]
    out = evaluate_consensus(obs, evaluated_at=datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc))
    assert out.status == ConsensusStatus.NO_CONSENSUS

def test_case4_exact_boundary():
    obs = [make_obs("A", 100), make_obs("B", 105), make_obs("C", 110)]
    out = evaluate_consensus(obs, evaluated_at=datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc))
    assert out.status == ConsensusStatus.REACHED
    assert len(out.accepted_sources) == 3
    assert out.consensus_value_mm == 105.0

def test_case5_just_outside_boundary():
    obs = [make_obs("A", 100), make_obs("B", 110.02)]
    out = evaluate_consensus(obs, evaluated_at=datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc))
    assert out.status == ConsensusStatus.NO_CONSENSUS

def test_case6_two_source_quorum():
    obs = [make_obs("A", 100), make_obs("B", 101)]
    out = evaluate_consensus(obs, evaluated_at=datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc))
    assert out.status == ConsensusStatus.REACHED
    assert len(out.accepted_sources) == 2
    assert out.consensus_value_mm == 100.5

def test_duplicate_source_ids():
    obs = [make_obs("A", 100), make_obs("A", 100)]
    out = evaluate_consensus(obs, evaluated_at=datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc))
    assert out.status == ConsensusStatus.NO_CONSENSUS
    assert out.source_count_accepted == 1

def test_conflicting_duplicate_source_ids():
    obs = [make_obs("A", 100), make_obs("A", 50)]
    out = evaluate_consensus(obs, evaluated_at=datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc))
    assert out.status == ConsensusStatus.NO_CONSENSUS

def test_duplicate_plus_valid_quorum():
    # A=100, A=100, B=102, C=104
    obs = [make_obs("A", 100), make_obs("A", 100), make_obs("B", 102), make_obs("C", 104)]
    out = evaluate_consensus(obs, evaluated_at=datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc))
    assert out.status == ConsensusStatus.REACHED
    assert len(out.accepted_sources) == 3
    assert out.consensus_value_mm == 102.0

def test_nan():
    obs = [make_obs("A", 110), make_obs("B", 108), make_obs("C", float('nan'))]
    out = evaluate_consensus(obs, evaluated_at=datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc))
    assert out.status == ConsensusStatus.REACHED
    assert out.consensus_value_mm == 109.0
    assert "C" not in out.accepted_sources
    assert "C" not in out.outlier_sources # It was completely discarded

def test_positive_infinity():
    obs = [make_obs("A", 110), make_obs("B", 108), make_obs("C", float('inf'))]
    out = evaluate_consensus(obs, evaluated_at=datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc))
    assert out.status == ConsensusStatus.REACHED
    assert out.consensus_value_mm == 109.0

def test_negative_infinity():
    obs = [make_obs("A", 110), make_obs("B", 108), make_obs("C", float('-inf'))]
    out = evaluate_consensus(obs, evaluated_at=datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc))
    assert out.status == ConsensusStatus.REACHED
    assert out.consensus_value_mm == 109.0

def test_negative_rainfall():
    obs = [make_obs("A", 110), make_obs("B", 108), make_obs("C", -10)]
    out = evaluate_consensus(obs, evaluated_at=datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc))
    assert out.status == ConsensusStatus.REACHED
    assert out.consensus_value_mm == 109.0

def test_invalid_values_plus_valid_quorum():
    obs = [make_obs("A", 100), make_obs("B", 101), make_obs("C", -5), make_obs("D", float('nan'))]
    out = evaluate_consensus(obs, evaluated_at=datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc))
    assert out.status == ConsensusStatus.REACHED
    assert out.consensus_value_mm == 100.5
    assert len(out.accepted_sources) == 2

def test_fresh_observation():
    # age = 1000s, threshold = 7200s
    obs = [make_obs("A", 100, 1000), make_obs("B", 102, 1000)]
    out = evaluate_consensus(obs, stale_threshold_seconds=7200, evaluated_at=datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc))
    assert out.status == ConsensusStatus.REACHED

def test_exactly_at_freshness_boundary():
    obs = [make_obs("A", 100, 7200), make_obs("B", 102, 7200)]
    out = evaluate_consensus(obs, stale_threshold_seconds=7200, evaluated_at=datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc))
    assert out.status == ConsensusStatus.REACHED

def test_stale_observation():
    obs = [make_obs("A", 100, 7201), make_obs("B", 102, 7201)]
    out = evaluate_consensus(obs, stale_threshold_seconds=7200, evaluated_at=datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc))
    assert out.status == ConsensusStatus.NO_CONSENSUS

def test_mixed_fresh_stale_observations():
    obs = [make_obs("A", 100, 1000), make_obs("B", 102, 1000), make_obs("C", 104, 8000)]
    out = evaluate_consensus(obs, stale_threshold_seconds=7200, evaluated_at=datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc))
    assert out.status == ConsensusStatus.REACHED
    assert len(out.accepted_sources) == 2
    assert "C" not in out.accepted_sources

def test_deterministic_repeated_execution():
    obs = [make_obs("A", 100), make_obs("B", 102), make_obs("C", 50)]
    eval_at = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    out1 = evaluate_consensus(obs, evaluated_at=eval_at)
    out2 = evaluate_consensus(obs, evaluated_at=eval_at)
    out3 = evaluate_consensus(obs, evaluated_at=eval_at)
    
    assert out1.status == out2.status == out3.status == ConsensusStatus.REACHED
    assert out1.consensus_value_mm == out2.consensus_value_mm == out3.consensus_value_mm == 101.0
    assert out1.accepted_sources == out2.accepted_sources == out3.accepted_sources
    assert out1.outlier_sources == out2.outlier_sources == out3.outlier_sources

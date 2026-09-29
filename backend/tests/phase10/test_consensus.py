import pytest
from datetime import datetime, timezone
from services.consensus import evaluate_consensus, SourceObservation, ConsensusStatus

def test_consensus_three_agree():
    now = datetime.now(timezone.utc)
    obs = [
        SourceObservation("src1", 110.0, observed_at=now),
        SourceObservation("src2", 108.0, observed_at=now),
        SourceObservation("src3", 111.0, observed_at=now),
    ]
    result = evaluate_consensus(obs)
    assert result.status == ConsensusStatus.REACHED
    assert result.consensus_value_mm == 110.0
    assert len(result.accepted_sources) == 3

def test_consensus_two_agree():
    now = datetime.now(timezone.utc)
    obs = [
        SourceObservation("src1", 110.0, observed_at=now),
        SourceObservation("src2", 110.0, observed_at=now),
    ]
    result = evaluate_consensus(obs)
    assert result.status == ConsensusStatus.REACHED
    assert result.consensus_value_mm == 110.0
    assert len(result.accepted_sources) == 2

def test_consensus_mutually_inconsistent():
    now = datetime.now(timezone.utc)
    obs = [
        SourceObservation("src1", 90.0, observed_at=now),
        SourceObservation("src2", 100.0, observed_at=now),
        SourceObservation("src3", 110.0, observed_at=now),
    ]
    result = evaluate_consensus(obs)
    assert result.status == ConsensusStatus.NO_CONSENSUS
    assert result.consensus_value_mm is None

def test_consensus_one_extreme_outlier():
    now = datetime.now(timezone.utc)
    obs = [
        SourceObservation("src1", 100.0, observed_at=now),
        SourceObservation("src2", 102.0, observed_at=now),
        SourceObservation("src3", 500.0, observed_at=now),
    ]
    result = evaluate_consensus(obs)
    assert result.status == ConsensusStatus.REACHED
    assert result.consensus_value_mm == 101.0
    assert len(result.accepted_sources) == 2
    assert "src3" in result.outlier_sources

def test_consensus_insufficient_quorum():
    now = datetime.now(timezone.utc)
    obs = [
        SourceObservation("src1", 100.0, observed_at=now)
    ]
    result = evaluate_consensus(obs)
    assert result.status == ConsensusStatus.NO_CONSENSUS

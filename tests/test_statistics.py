"""
Unit tests for statistical distributions and rankings.
"""

import pytest
import pandas as pd
from src.statistics.performance_metrics import compute_distribution_summary, compute_correlation_matrix

def test_distribution_summary():
    data = [10, 20, 30, 40, 50]
    summary = compute_distribution_summary(data)
    assert summary["count"] == 5
    assert summary["mean"] == 30.0
    assert summary["median"] == 30.0
    assert summary["min"] == 10.0
    assert summary["max"] == 50.0

def test_correlation_matrix():
    df = pd.DataFrame({
        "runs": [10, 20, 30, 40, 50],
        "balls": [8, 15, 22, 28, 35],
        "fours": [1, 2, 3, 4, 5]
    })
    corr = compute_correlation_matrix(df, ["runs", "balls", "fours"])
    assert corr.shape == (3, 3)
    assert corr.loc["runs", "runs"] == 1.0
    assert corr.loc["runs", "balls"] > 0.9

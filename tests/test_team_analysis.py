"""
Unit tests for team performance, season analysis, and team comparisons.
"""

import pytest
import pandas as pd
from src.team_analysis.team_performance import TeamPerformance
from src.team_analysis.season_analysis import SeasonAnalysis
from src.team_analysis.team_comparison import TeamComparison

@pytest.fixture
def mock_matches():
    return pd.DataFrame([
        {
            "match_id": 1, "season": "2023", "team1": "CSK", "team2": "MI",
            "winner": "CSK", "result": "runs", "win_by_runs": 20, "win_by_wickets": 0,
            "toss_winner": "CSK", "toss_decision": "bat", "margin_display": "20 runs"
        },
        {
            "match_id": 2, "season": "2023", "team1": "CSK", "team2": "MI",
            "winner": "MI", "result": "wickets", "win_by_runs": 0, "win_by_wickets": 6,
            "toss_winner": "MI", "toss_decision": "field", "margin_display": "6 wickets"
        }
    ])

def test_team_performance(mock_matches):
    team_perf = TeamPerformance(mock_matches)
    summary = team_perf.get_all_teams_summary()

    assert len(summary) == 2
    csk = summary[summary["Team"] == "CSK"].iloc[0]
    assert csk["Matches"] == 2
    assert csk["Wins"] == 1
    assert csk["Losses"] == 1
    assert csk["Win %"] == 50.0

def test_head_to_head(mock_matches):
    comp = TeamComparison(mock_matches)
    h2h = comp.get_head_to_head("CSK", "MI")

    assert h2h["total_matches"] == 2
    assert h2h["team1_wins"] == 1
    assert h2h["team2_wins"] == 1
    assert h2h["team1_win_pct"] == 50.0

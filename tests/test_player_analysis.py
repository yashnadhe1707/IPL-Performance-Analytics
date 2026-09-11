"""
Unit tests for batting analysis, bowling analysis, and player comparisons.
"""

import pytest
import pandas as pd
from src.player_analysis.batting_analysis import BattingAnalysis
from src.player_analysis.bowling_analysis import BowlingAnalysis
from src.player_analysis.player_comparison import PlayerComparison

@pytest.fixture
def mock_deliveries():
    return pd.DataFrame([
        {
            "match_id": 1, "inning": 1, "batting_team": "RCB", "bowling_team": "CSK",
            "over": 1, "ball": 1, "batsman": "Virat Kohli", "bowler": "Deepak Chahar",
            "batsman_runs": 4, "extra_runs": 0, "total_runs": 4, "wide_runs": 0, "noball_runs": 0,
            "is_wicket": 0, "is_bowler_wicket": 0, "player_dismissed": None, "season": "2023"
        },
        {
            "match_id": 1, "inning": 1, "batting_team": "RCB", "bowling_team": "CSK",
            "over": 1, "ball": 2, "batsman": "Virat Kohli", "bowler": "Deepak Chahar",
            "batsman_runs": 6, "extra_runs": 0, "total_runs": 6, "wide_runs": 0, "noball_runs": 0,
            "is_wicket": 0, "is_bowler_wicket": 0, "player_dismissed": None, "season": "2023"
        },
        {
            "match_id": 1, "inning": 1, "batting_team": "RCB", "bowling_team": "CSK",
            "over": 1, "ball": 3, "batsman": "Virat Kohli", "bowler": "Deepak Chahar",
            "batsman_runs": 0, "extra_runs": 0, "total_runs": 0, "wide_runs": 0, "noball_runs": 0,
            "is_wicket": 1, "is_bowler_wicket": 1, "player_dismissed": "Virat Kohli", "season": "2023"
        }
    ])

def test_batting_metrics(mock_deliveries):
    batting = BattingAnalysis(mock_deliveries)
    summary = batting.get_all_batsmen_summary()

    assert not summary.empty
    vk = summary[summary["Batsman"] == "Virat Kohli"].iloc[0]
    assert vk["Runs"] == 10
    assert vk["Balls"] == 3
    assert vk["Fours"] == 1
    assert vk["Sixes"] == 1
    assert vk["Dismissals"] == 1
    assert vk["Average"] == 10.0
    assert vk["Strike Rate"] == round((10 / 3) * 100, 2)

def test_bowling_metrics(mock_deliveries):
    bowling = BowlingAnalysis(mock_deliveries)
    summary = bowling.get_all_bowlers_summary()

    assert not summary.empty
    dc = summary[summary["Bowler"] == "Deepak Chahar"].iloc[0]
    assert dc["Wickets"] == 1
    assert dc["Balls"] == 3
    assert dc["Runs Conceded"] == 10
    assert dc["Best Bowling"] == "1/10"

def test_player_comparison(mock_deliveries):
    comp = PlayerComparison(mock_deliveries)
    df_comp = comp.compare_batsmen(["Virat Kohli"])
    assert len(df_comp) == 1
    assert df_comp["Batsman"].iloc[0] == "Virat Kohli"

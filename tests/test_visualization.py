"""
Unit tests for Plotly visualization generation.
"""

import pytest
import pandas as pd
from src.visualization.player_charts import plot_top_batsmen_bar, plot_runs_vs_strike_rate
from src.visualization.team_charts import plot_team_win_percentages

def test_player_charts():
    df_batsmen = pd.DataFrame([
        {"Batsman": "Virat Kohli", "Runs": 700, "Balls": 500, "Strike Rate": 140.0, "Average": 50.0, "Sixes": 30},
        {"Batsman": "Rohit Sharma", "Runs": 600, "Balls": 450, "Strike Rate": 133.3, "Average": 40.0, "Sixes": 25}
    ])
    fig1 = plot_top_batsmen_bar(df_batsmen)
    assert fig1 is not None
    assert len(fig1.data) > 0

    fig2 = plot_runs_vs_strike_rate(df_batsmen)
    assert fig2 is not None
    assert len(fig2.data) > 0

def test_team_charts():
    df_teams = pd.DataFrame([
        {"Team": "CSK", "Win %": 60.0, "Wins": 12, "Matches": 20},
        {"Team": "MI", "Win %": 55.0, "Wins": 11, "Matches": 20}
    ])
    fig = plot_team_win_percentages(df_teams)
    assert fig is not None
    assert len(fig.data) > 0

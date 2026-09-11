"""
Unit tests for factual data-driven insight generation.
"""

import pytest
import pandas as pd
from src.insights.insight_generator import InsightGenerator

def test_insight_generator():
    matches = pd.DataFrame([
        {
            "match_id": 1, "season": "2023", "team1": "CSK", "team2": "GT",
            "winner": "CSK", "result": "wickets", "win_by_runs": 0, "win_by_wickets": 5,
            "toss_winner": "CSK", "toss_decision": "field", "venue": "Narendra Modi Stadium",
            "player_of_match": "Devon Conway", "margin_display": "5 wickets"
        }
    ])
    deliveries = pd.DataFrame([
        {
            "match_id": 1, "inning": 1, "batting_team": "GT", "bowling_team": "CSK",
            "over": 1, "ball": 1, "batsman": "Shubman Gill", "bowler": "Deepak Chahar",
            "batsman_runs": 4, "extra_runs": 0, "total_runs": 4, "wide_runs": 0, "noball_runs": 0,
            "is_wicket": 0, "is_bowler_wicket": 0, "player_dismissed": None, "season": "2023",
            "venue": "Narendra Modi Stadium"
        }
    ])

    gen = InsightGenerator(matches, deliveries)
    insights = gen.generate_all_insights()

    assert "tournament" in insights
    assert "batting" in insights
    assert "teams" in insights
    assert len(insights["tournament"]) > 0

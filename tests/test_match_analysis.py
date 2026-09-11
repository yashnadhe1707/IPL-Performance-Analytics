"""
Unit tests for match scorecards, toss analytics, and venue analytics.
"""

import pytest
import pandas as pd
from src.match_analysis.match_analysis import MatchAnalysis
from src.match_analysis.toss_analysis import TossAnalysis
from src.match_analysis.venue_analysis import VenueAnalysis

@pytest.fixture
def mock_match_data():
    matches = pd.DataFrame([
        {
            "match_id": 101, "season": "2022", "team1": "KKR", "team2": "RR",
            "venue": "Eden Gardens", "toss_winner": "KKR", "toss_decision": "field",
            "winner": "KKR", "result": "wickets", "win_by_runs": 0, "win_by_wickets": 7,
            "player_of_match": "Andre Russell", "margin_display": "7 wickets"
        },
        {
            "match_id": 102, "season": "2022", "team1": "KKR", "team2": "RR",
            "venue": "Eden Gardens", "toss_winner": "RR", "toss_decision": "bat",
            "winner": "RR", "result": "runs", "win_by_runs": 15, "win_by_wickets": 0,
            "player_of_match": "Sanju Samson", "margin_display": "15 runs"
        }
    ])
    return matches

def test_toss_analysis(mock_match_data):
    toss = TossAnalysis(mock_match_data)
    dist = toss.get_toss_decision_distribution()
    assert dist["total_tosses"] == 2
    assert dist["field_count"] == 1
    assert dist["bat_count"] == 1
    assert dist["field_pct"] == 50.0

    assoc = toss.get_toss_winner_match_winner_association()
    assert assoc["total_matches"] == 2
    assert assoc["association_percentage"] == 100.0

def test_venue_analysis(mock_match_data):
    venue = VenueAnalysis(mock_match_data)
    summary = venue.get_all_venues_summary()
    assert len(summary) == 1
    assert summary["Venue"].iloc[0] == "Eden Gardens"
    assert summary["Matches"].iloc[0] == 2
    assert summary["Batting 1st Wins"].iloc[0] == 1
    assert summary["Batting 2nd Wins"].iloc[0] == 1

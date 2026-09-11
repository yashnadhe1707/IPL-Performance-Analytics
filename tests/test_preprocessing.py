"""
Unit tests for data loader and data cleaner modules.
"""

import pytest
import pandas as pd
import numpy as np
from src.utils.helpers import safe_divide, standardize_team_name, standardize_player_name
from src.preprocessing.data_cleaner import IPLCleaner

def test_safe_divide():
    assert safe_divide(10, 2) == 5.0
    assert safe_divide(10, 0) == 0.0
    assert safe_divide(None, 5) == 0.0
    assert safe_divide(10, None) == 0.0
    assert safe_divide(0, 5) == 0.0

def test_standardize_team_name():
    assert standardize_team_name("Delhi Daredevils") == "Delhi Capitals"
    assert standardize_team_name("Kings XI Punjab") == "Punjab Kings"
    assert standardize_team_name("Rising Pune Supergiants") == "Rising Pune Supergiant"
    assert standardize_team_name("Mumbai Indians") == "Mumbai Indians"

def test_standardize_player_name():
    assert standardize_player_name("  Virat   Kohli  ") == "Virat Kohli"
    assert standardize_player_name(None) == "Unknown Player"

def test_cleaner_pipeline():
    sample_matches = pd.DataFrame([{
        "id": 1,
        "season": "2022/23",
        "date": "2022-04-10",
        "team1": "Delhi Daredevils",
        "team2": "Mumbai Indians",
        "toss_winner": "Delhi Daredevils",
        "toss_decision": "Field",
        "winner": "Delhi Daredevils",
        "win_by_runs": 0,
        "win_by_wickets": 5,
        "player_of_match": " Rishabh Pant ",
        "venue": "Wankhede Stadium"
    }])

    sample_deliveries = pd.DataFrame([
        {
            "match_id": 1,
            "inning": 1,
            "batting_team": "Mumbai Indians",
            "bowling_team": "Delhi Daredevils",
            "over": 1,
            "ball": 1,
            "batsman": "Rohit Sharma",
            "bowler": "Anrich Nortje",
            "batsman_runs": 4,
            "extra_runs": 0,
            "total_runs": 4,
            "is_wicket": 0
        },
        {
            "match_id": 1,
            "inning": 1,
            "batting_team": "Mumbai Indians",
            "bowling_team": "Delhi Daredevils",
            "over": 1,
            "ball": 2,
            "batsman": "Rohit Sharma",
            "bowler": "Anrich Nortje",
            "batsman_runs": 0,
            "extra_runs": 0,
            "total_runs": 0,
            "is_wicket": 1,
            "dismissal_kind": "bowled",
            "player_dismissed": "Rohit Sharma"
        }
    ])

    cleaner = IPLCleaner()
    cm, cd = cleaner.clean_pipeline(sample_matches, sample_deliveries)

    assert cm["team1"].iloc[0] == "Delhi Capitals"
    assert cm["player_of_match"].iloc[0] == "Rishabh Pant"
    assert cd["is_four"].iloc[0] == 1
    assert cd["is_bowler_wicket"].iloc[1] == 1
    assert cd["over_phase"].iloc[0] == "Powerplay"

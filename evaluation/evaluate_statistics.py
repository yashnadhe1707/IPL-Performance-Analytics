"""
Statistics Validation Evaluation Script.
Validates computed batting, bowling, team, and toss metrics against
ground-truth calculations and mathematical definitions.
"""

import os
import json
import sys
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.preprocessing.data_loader import IPLDataLoader
from src.player_analysis.batting_analysis import BattingAnalysis
from src.player_analysis.bowling_analysis import BowlingAnalysis
from src.team_analysis.team_performance import TeamPerformance
from src.match_analysis.toss_analysis import TossAnalysis

def run_statistics_evaluation():
    loader = IPLDataLoader()
    df_matches, df_deliveries = loader.load_processed_data()
    if df_matches is None or df_deliveries is None:
        raw_m, raw_d = loader.load_raw_data()
        from src.preprocessing.data_cleaner import IPLCleaner
        df_matches, df_deliveries = IPLCleaner().clean_pipeline(raw_m, raw_d)

    batting = BattingAnalysis(df_deliveries, df_matches)
    bowling = BowlingAnalysis(df_deliveries, df_matches)
    team_perf = TeamPerformance(df_matches, df_deliveries)
    toss = TossAnalysis(df_matches)

    # 1. Validate Batting Totals
    df_batsmen = batting.get_all_batsmen_summary()
    total_batsman_runs_engine = int(df_batsmen["Runs"].sum())
    ground_truth_batsman_runs = int(df_deliveries["batsman_runs"].sum())
    batting_runs_match = (total_batsman_runs_engine == ground_truth_batsman_runs)

    # 2. Validate Bowling Wickets
    df_bowlers = bowling.get_all_bowlers_summary()
    total_bowler_wickets_engine = int(df_bowlers["Wickets"].sum())
    ground_truth_bowler_wickets = int(df_deliveries["is_bowler_wicket"].sum())
    bowling_wickets_match = (total_bowler_wickets_engine == ground_truth_bowler_wickets)

    # 3. Validate Team Win Totals
    df_teams = team_perf.get_all_teams_summary()
    team_wins_engine = int(df_teams["Wins"].sum())
    valid_winners_count = int(df_matches[df_matches["winner"].notna() & (df_matches["winner"] != "")]["winner"].count())
    team_wins_match = (team_wins_engine == valid_winners_count)

    # 4. Validate Win Percentages Bounds (0 to 100)
    win_pct_bounds = bool((df_teams["Win %"] >= 0).all() and (df_teams["Win %"] <= 100).all())

    # 5. Validate Toss Percentages Sum (~100%)
    toss_dist = toss.get_toss_decision_distribution()
    toss_pct_sum = round(toss_dist["field_pct"] + toss_dist["bat_pct"], 1)
    toss_sum_match = (toss_pct_sum == 100.0)

    report = {
        "batting_runs_validation": {
            "engine_calculated_runs": total_batsman_runs_engine,
            "raw_deliveries_runs": ground_truth_batsman_runs,
            "is_exact_match": batting_runs_match
        },
        "bowling_wickets_validation": {
            "engine_calculated_wickets": total_bowler_wickets_engine,
            "raw_deliveries_wickets": ground_truth_bowler_wickets,
            "is_exact_match": bowling_wickets_match
        },
        "team_wins_validation": {
            "engine_calculated_team_wins": team_wins_engine,
            "matches_with_winners_count": valid_winners_count,
            "is_exact_match": team_wins_match,
            "all_win_percentages_within_bounds": win_pct_bounds
        },
        "toss_statistics_validation": {
            "toss_field_pct": toss_dist["field_pct"],
            "toss_bat_pct": toss_dist["bat_pct"],
            "percentages_sum_to_100": toss_sum_match
        },
        "overall_validation_status": "PASSED" if (batting_runs_match and bowling_wickets_match and team_wins_match and toss_sum_match) else "FAILED"
    }

    out_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "outputs", "evaluation_results"))
    os.makedirs(out_dir, exist_ok=True)
    report_path = os.path.join(out_dir, "statistics_validation_report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=4)

    print("Statistics Validation Completed Successfully.")
    print(f"Report saved to: {report_path}")
    print(json.dumps(report, indent=2))
    return report

if __name__ == "__main__":
    run_statistics_evaluation()

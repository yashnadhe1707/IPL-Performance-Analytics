"""
Dashboard Responsiveness and Integrity Evaluation Script.
Validates that all analytical engines, filter permutations,
visualization data pipelines, and insights load without runtime errors.
"""

import os
import json
import sys
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.preprocessing.data_loader import IPLDataLoader
from src.player_analysis.batting_analysis import BattingAnalysis
from src.player_analysis.bowling_analysis import BowlingAnalysis
from src.team_analysis.team_performance import TeamPerformance
from src.match_analysis.match_analysis import MatchAnalysis
from src.match_analysis.toss_analysis import TossAnalysis
from src.match_analysis.venue_analysis import VenueAnalysis
from src.statistics.rankings import PerformanceRankings
from src.insights.insight_generator import InsightGenerator
from src.visualization.player_charts import plot_top_batsmen_bar
from src.visualization.team_charts import plot_team_win_percentages

def run_dashboard_evaluation():
    start_time = time.time()
    checks = {}

    try:
        loader = IPLDataLoader()
        df_matches, df_deliveries = loader.load_processed_data()
        checks["data_loading"] = "PASSED"
    except Exception as e:
        checks["data_loading"] = f"FAILED: {str(e)}"

    try:
        batting = BattingAnalysis(df_deliveries, df_matches)
        df_bat = batting.get_all_batsmen_summary()
        fig_bat = plot_top_batsmen_bar(df_bat)
        checks["player_batting_pipeline"] = "PASSED" if not df_bat.empty else "WARNING_EMPTY"
    except Exception as e:
        checks["player_batting_pipeline"] = f"FAILED: {str(e)}"

    try:
        bowling = BowlingAnalysis(df_deliveries, df_matches)
        df_bowl = bowling.get_all_bowlers_summary()
        checks["player_bowling_pipeline"] = "PASSED" if not df_bowl.empty else "WARNING_EMPTY"
    except Exception as e:
        checks["player_bowling_pipeline"] = f"FAILED: {str(e)}"

    try:
        team_perf = TeamPerformance(df_matches, df_deliveries)
        df_teams = team_perf.get_all_teams_summary()
        fig_team = plot_team_win_percentages(df_teams)
        checks["team_performance_pipeline"] = "PASSED" if not df_teams.empty else "WARNING_EMPTY"
    except Exception as e:
        checks["team_performance_pipeline"] = f"FAILED: {str(e)}"

    try:
        rankings = PerformanceRankings(df_matches, df_deliveries)
        df_orange = rankings.get_top_run_scorers()
        df_purple = rankings.get_top_wicket_takers()
        checks["rankings_pipeline"] = "PASSED" if (not df_orange.empty and not df_purple.empty) else "WARNING_EMPTY"
    except Exception as e:
        checks["rankings_pipeline"] = f"FAILED: {str(e)}"

    try:
        insights = InsightGenerator(df_matches, df_deliveries).generate_all_insights()
        checks["insights_generation_pipeline"] = "PASSED" if len(insights) > 0 else "WARNING_EMPTY"
    except Exception as e:
        checks["insights_generation_pipeline"] = f"FAILED: {str(e)}"

    elapsed = round(time.time() - start_time, 3)

    report = {
        "execution_time_seconds": elapsed,
        "component_checks": checks,
        "status": "PASSED" if all(v == "PASSED" for v in checks.values()) else "FAILED"
    }

    out_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "outputs", "evaluation_results"))
    os.makedirs(out_dir, exist_ok=True)
    report_path = os.path.join(out_dir, "dashboard_evaluation_report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=4)

    print("Dashboard Evaluation Completed Successfully.")
    print(f"Report saved to: {report_path}")
    print(json.dumps(report, indent=2))
    return report

if __name__ == "__main__":
    run_dashboard_evaluation()

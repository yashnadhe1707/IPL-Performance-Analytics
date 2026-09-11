"""
Team Comparison Module.
Enables head-to-head match-up analysis between two teams
and multi-team statistical benchmarking across historical seasons.
"""

from typing import Dict, List, Optional
import pandas as pd
import numpy as np
from src.utils.helpers import safe_divide
from src.team_analysis.team_performance import TeamPerformance

class TeamComparison:
    def __init__(self, df_matches: pd.DataFrame, df_deliveries: Optional[pd.DataFrame] = None):
        self.df_matches = df_matches.copy()
        self.df_deliveries = df_deliveries.copy() if df_deliveries is not None else None
        self.team_perf = TeamPerformance(df_matches, df_deliveries)

    def get_head_to_head(self, team1: str, team2: str) -> Dict:
        """
        Analyzes head-to-head historical encounters between team1 and team2.
        """
        df_m = self.df_matches[
            ((self.df_matches["team1"] == team1) & (self.df_matches["team2"] == team2)) |
            ((self.df_matches["team1"] == team2) & (self.df_matches["team2"] == team1))
        ]

        if df_m.empty:
            return {"error": f"No matches played between {team1} and {team2}"}

        total_matches = len(df_m)
        t1_wins = len(df_m[df_m["winner"] == team1])
        t2_wins = len(df_m[df_m["winner"] == team2])
        ties = total_matches - t1_wins - t2_wins

        t1_win_pct = safe_divide(t1_wins * 100, total_matches)
        t2_win_pct = safe_divide(t2_wins * 100, total_matches)

        # Average and highest scores against each other
        t1_scores = []
        t2_scores = []
        if self.df_deliveries is not None:
            match_ids = df_m["match_id"].unique()
            h2h_deliv = self.df_deliveries[self.df_deliveries["match_id"].isin(match_ids)]
            inn_scores = h2h_deliv.groupby(["match_id", "batting_team"])["total_runs"].sum().reset_index()
            t1_scores = inn_scores[inn_scores["batting_team"] == team1]["total_runs"].tolist()
            t2_scores = inn_scores[inn_scores["batting_team"] == team2]["total_runs"].tolist()

        res = {
            "team1": team1,
            "team2": team2,
            "total_matches": total_matches,
            "team1_wins": t1_wins,
            "team2_wins": t2_wins,
            "ties_or_no_result": ties,
            "team1_win_pct": t1_win_pct,
            "team2_win_pct": t2_win_pct,
            "team1_avg_score": round(float(np.mean(t1_scores)), 1) if t1_scores else 0.0,
            "team2_avg_score": round(float(np.mean(t2_scores)), 1) if t2_scores else 0.0,
            "team1_high_score": max(t1_scores) if t1_scores else 0,
            "team2_high_score": max(t2_scores) if t2_scores else 0,
            "recent_matches": [r for r in df_m[[c for c in ["season", "date", "venue", "toss_winner", "toss_decision", "winner", "margin_display"] if c in df_m.columns]].head(10).to_dict(orient="records")]
        }
        return res

    def compare_multiple_teams(self, teams: List[str]) -> pd.DataFrame:
        all_teams = self.team_perf.get_all_teams_summary()
        if all_teams.empty:
            return pd.DataFrame()
        matched = all_teams[all_teams["Team"].isin(teams)].copy()
        return matched.reset_index(drop=True)

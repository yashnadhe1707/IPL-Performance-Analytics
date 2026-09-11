"""
Season Analysis Module.
Generates season standings, points tables, scoring trends,
and tournament-level statistics across historical IPL editions.
"""

from typing import Dict, List, Optional
import pandas as pd
import numpy as np
from src.utils.helpers import safe_divide
from src.team_analysis.team_performance import TeamPerformance

class SeasonAnalysis:
    def __init__(self, df_matches: pd.DataFrame, df_deliveries: Optional[pd.DataFrame] = None):
        self.df_matches = df_matches.copy()
        self.df_deliveries = df_deliveries.copy() if df_deliveries is not None else None
        self.team_perf = TeamPerformance(df_matches, df_deliveries)

    def get_available_seasons(self) -> List[str]:
        if "season" in self.df_matches.columns:
            return sorted(self.df_matches["season"].dropna().unique().astype(str).tolist())
        return []

    def get_season_standings(self, season: str) -> pd.DataFrame:
        df_summary = self.team_perf.get_all_teams_summary(season=season)
        if df_summary.empty:
            return pd.DataFrame()

        # Points: 2 points per win, 1 point per tie/NR
        df_summary["Points"] = (df_summary["Wins"] * 2) + (df_summary["Ties/NR"] * 1)
        standings = df_summary.sort_values(by=["Points", "Win %", "Wins"], ascending=[False, False, False]).reset_index(drop=True)
        standings.index = standings.index + 1
        standings.index.name = "Rank"
        return standings.reset_index()

    def get_season_overview_kpis(self, season: str) -> Dict:
        df_m = self.df_matches[self.df_matches["season"].astype(str) == str(season)]
        if df_m.empty:
            return {}

        total_matches = len(df_m)
        all_teams = set(df_m["team1"].dropna().unique()).union(set(df_m["team2"].dropna().unique()))
        
        kpis = {
            "Season": str(season),
            "Total Matches": total_matches,
            "Teams Participating": len(all_teams)
        }

        if self.df_deliveries is not None and "season" in self.df_deliveries.columns:
            deliv = self.df_deliveries[self.df_deliveries["season"].astype(str) == str(season)]
            total_runs = int(deliv["total_runs"].sum())
            total_wickets = int(deliv["is_bowler_wicket"].sum()) if "is_bowler_wicket" in deliv.columns else int(deliv["is_wicket"].sum())
            total_sixes = int(deliv["is_six"].sum()) if "is_six" in deliv.columns else int((deliv["batsman_runs"] == 6).sum())
            total_fours = int(deliv["is_four"].sum()) if "is_four" in deliv.columns else int((deliv["batsman_runs"] == 4).sum())

            # Innings scores
            inn_totals = deliv.groupby(["match_id", "inning"])["total_runs"].sum()
            avg_inn_score = round(float(inn_totals.mean()), 1) if not inn_totals.empty else 0.0
            highest_score = int(inn_totals.max()) if not inn_totals.empty else 0

            kpis.update({
                "Total Runs": total_runs,
                "Total Wickets": total_wickets,
                "Total Sixes": total_sixes,
                "Total Fours": total_fours,
                "Average Innings Score": avg_inn_score,
                "Highest Innings Score": highest_score
            })

        return kpis

    def get_all_seasons_trend(self) -> pd.DataFrame:
        seasons = self.get_available_seasons()
        trends = []
        for s in seasons:
            kpi = self.get_season_overview_kpis(s)
            if kpi:
                trends.append(kpi)
        res_df = pd.DataFrame(trends)
        if not res_df.empty:
            res_df = res_df.sort_values(by="Season").reset_index(drop=True)
        return res_df

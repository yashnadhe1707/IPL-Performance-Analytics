"""
Venue Analysis Module.
Examines stadium characteristics including scoring averages,
chasing vs defending advantages, highest totals, and team venue records.
"""

from typing import Dict, List, Optional
import pandas as pd
import numpy as np
from src.utils.helpers import safe_divide

class VenueAnalysis:
    def __init__(self, df_matches: pd.DataFrame, df_deliveries: Optional[pd.DataFrame] = None):
        self.df_matches = df_matches.copy()
        self.df_deliveries = df_deliveries.copy() if df_deliveries is not None else None

    def get_all_venues_summary(self) -> pd.DataFrame:
        df = self.df_matches.copy()
        if "venue" not in df.columns or df.empty:
            return pd.DataFrame()

        # Venue scoring averages if deliveries are available
        venue_avg_scores = {}
        venue_high_scores = {}
        if self.df_deliveries is not None and "venue" in self.df_deliveries.columns:
            inn_scores = self.df_deliveries.groupby(["venue", "match_id", "inning"])["total_runs"].sum().reset_index()
            for v, grp in inn_scores.groupby("venue"):
                venue_avg_scores[v] = round(float(grp["total_runs"].mean()), 1)
                venue_high_scores[v] = int(grp["total_runs"].max())

        records = []
        for venue, v_df in df.groupby("venue"):
            total_matches = len(v_df)
            if total_matches == 0:
                continue

            # Batting 1st vs Batting 2nd wins
            # win_by_runs > 0 indicates team batting first won
            # win_by_wickets > 0 indicates team batting second won
            bat_1st_wins = int((v_df["win_by_runs"] > 0).sum())
            bat_2nd_wins = int((v_df["win_by_wickets"] > 0).sum())
            ties = total_matches - bat_1st_wins - bat_2nd_wins

            bat_1st_win_pct = safe_divide(bat_1st_wins * 100, total_matches)
            bat_2nd_win_pct = safe_divide(bat_2nd_wins * 100, total_matches)

            # Most successful team at venue
            top_team = v_df["winner"].mode()[0] if not v_df["winner"].dropna().empty else "N/A"
            top_team_wins = int((v_df["winner"] == top_team).sum())

            records.append({
                "Venue": venue,
                "Matches": total_matches,
                "Batting 1st Wins": bat_1st_wins,
                "Batting 2nd Wins": bat_2nd_wins,
                "Batting 1st Win %": bat_1st_win_pct,
                "Batting 2nd Win %": bat_2nd_win_pct,
                "Avg Innings Score": venue_avg_scores.get(venue, 0.0),
                "Highest Score": venue_high_scores.get(venue, 0),
                "Top Team": top_team,
                "Top Team Wins": top_team_wins
            })

        res_df = pd.DataFrame(records)
        if not res_df.empty:
            res_df = res_df.sort_values(by="Matches", ascending=False).reset_index(drop=True)
        return res_df

    def get_venue_profile(self, venue_name: str) -> Dict:
        df = self.df_matches[self.df_matches["venue"] == venue_name]
        if df.empty:
            return {"error": f"No matches found for venue '{venue_name}'"}

        summary = self.get_all_venues_summary()
        v_row = summary[summary["Venue"] == venue_name]
        profile = v_row.iloc[0].to_dict() if not v_row.empty else {}

        # Team records at venue
        team_records = []
        all_teams = set(df["team1"].dropna().unique()).union(set(df["team2"].dropna().unique()))
        for t in all_teams:
            t_matches = len(df[(df["team1"] == t) | (df["team2"] == t)])
            t_wins = len(df[df["winner"] == t])
            team_records.append({
                "Team": t,
                "Matches": t_matches,
                "Wins": t_wins,
                "Win %": safe_divide(t_wins * 100, t_matches)
            })
        profile["team_records"] = sorted(team_records, key=lambda x: x["Wins"], reverse=True)

        return profile

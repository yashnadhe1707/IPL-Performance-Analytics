"""
Team Performance Analytics.
Calculates historical team metrics including matches, wins, losses,
win percentages, scoring averages, and highest/lowest totals.
"""

from typing import Dict, List, Optional
import pandas as pd
import numpy as np
from src.utils.helpers import safe_divide, standardize_team_name

class TeamPerformance:
    def __init__(self, df_matches: pd.DataFrame, df_deliveries: Optional[pd.DataFrame] = None):
        self.df_matches = df_matches.copy()
        self.df_deliveries = df_deliveries.copy() if df_deliveries is not None else None

    def _filter_matches(self, season: Optional[str] = None) -> pd.DataFrame:
        df = self.df_matches
        if season is not None and "season" in df.columns:
            df = df[df["season"].astype(str) == str(season)]
        return df

    def get_all_teams_summary(self, season: Optional[str] = None) -> pd.DataFrame:
        df_m = self._filter_matches(season=season)
        if df_m.empty:
            return pd.DataFrame()

        # Gather all distinct teams
        all_teams = sorted(list(set(df_m["team1"].dropna().unique()).union(set(df_m["team2"].dropna().unique()))))
        
        # Calculate team scores if deliveries are available
        team_high_scores = {}
        team_low_scores = {}
        team_avg_scores = {}

        if self.df_deliveries is not None:
            deliv = self.df_deliveries.copy()
            if season is not None and "season" in deliv.columns:
                deliv = deliv[deliv["season"].astype(str) == str(season)]
            
            inn_scores = deliv.groupby(["match_id", "batting_team"])["total_runs"].sum().reset_index()
            for t, grp in inn_scores.groupby("batting_team"):
                team_high_scores[t] = int(grp["total_runs"].max())
                team_low_scores[t] = int(grp["total_runs"].min())
                team_avg_scores[t] = round(float(grp["total_runs"].mean()), 1)

        records = []
        for team in all_teams:
            # Matches where team played
            team_matches = df_m[(df_m["team1"] == team) | (df_m["team2"] == team)]
            total_matches = len(team_matches)
            if total_matches == 0:
                continue

            wins = len(team_matches[team_matches["winner"] == team])
            ties = len(team_matches[team_matches["result"].isin(["tie", "super over", "no result"])])
            losses = total_matches - wins - ties
            win_pct = safe_divide(wins * 100, total_matches, default=0.0)
            loss_pct = safe_divide(losses * 100, total_matches, default=0.0)

            records.append({
                "Team": team,
                "Matches": total_matches,
                "Wins": wins,
                "Losses": losses,
                "Ties/NR": ties,
                "Win %": win_pct,
                "Loss %": loss_pct,
                "Average Score": team_avg_scores.get(team, 0.0),
                "Highest Score": team_high_scores.get(team, 0),
                "Lowest Score": team_low_scores.get(team, 0)
            })

        res_df = pd.DataFrame(records)
        if not res_df.empty:
            res_df = res_df.sort_values(by=["Win %", "Wins"], ascending=[False, False]).reset_index(drop=True)
        return res_df

    def get_team_profile(self, team_name: str) -> Dict:
        df_m = self.df_matches[(self.df_matches["team1"] == team_name) | (self.df_matches["team2"] == team_name)]
        if df_m.empty:
            return {"error": f"No match records found for {team_name}"}

        summary = self.get_all_teams_summary()
        t_row = summary[summary["Team"] == team_name]
        profile = t_row.iloc[0].to_dict() if not t_row.empty else {}

        # Batting 1st vs Chasing Record
        # Batting 1st: (toss_winner == team & toss_decision == 'bat') | (toss_winner != team & toss_decision == 'field')
        batting_first_matches = df_m[
            ((df_m["toss_winner"] == team_name) & (df_m["toss_decision"] == "bat")) |
            ((df_m["toss_winner"] != team_name) & (df_m["toss_decision"] == "field"))
        ]
        bat_1st_wins = len(batting_first_matches[batting_first_matches["winner"] == team_name])
        bat_1st_total = len(batting_first_matches)

        chasing_matches = df_m[
            ((df_m["toss_winner"] == team_name) & (df_m["toss_decision"] == "field")) |
            ((df_m["toss_winner"] != team_name) & (df_m["toss_decision"] == "bat"))
        ]
        chase_wins = len(chasing_matches[chasing_matches["winner"] == team_name])
        chase_total = len(chasing_matches)

        profile["batting_first"] = {
            "matches": bat_1st_total,
            "wins": bat_1st_wins,
            "win_pct": safe_divide(bat_1st_wins * 100, bat_1st_total)
        }
        profile["chasing"] = {
            "matches": chase_total,
            "wins": chase_wins,
            "win_pct": safe_divide(chase_wins * 100, chase_total)
        }

        # Season-wise performance trend
        season_perf = []
        for season, s_df in df_m.groupby("season"):
            s_matches = len(s_df)
            s_wins = len(s_df[s_df["winner"] == team_name])
            season_perf.append({
                "Season": str(season),
                "Matches": s_matches,
                "Wins": s_wins,
                "Win %": safe_divide(s_wins * 100, s_matches)
            })
        profile["season_trends"] = sorted(season_perf, key=lambda x: x["Season"])

        return profile

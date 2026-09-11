"""
Match Analysis Module.
Generates comprehensive match-level scorecards, innings progressions,
top player performances, and margin of victory distributions.
"""

from typing import Dict, List, Optional
import pandas as pd
import numpy as np
from src.utils.helpers import safe_divide, balls_to_overs_str

class MatchAnalysis:
    def __init__(self, df_matches: pd.DataFrame, df_deliveries: Optional[pd.DataFrame] = None):
        self.df_matches = df_matches.copy()
        self.df_deliveries = df_deliveries.copy() if df_deliveries is not None else None

    def get_matches_list(self, season: Optional[str] = None, team: Optional[str] = None) -> pd.DataFrame:
        df = self.df_matches.copy()
        if season is not None and "season" in df.columns:
            df = df[df["season"].astype(str) == str(season)]
        if team is not None:
            df = df[(df["team1"] == team) | (df["team2"] == team)]
        
        display_cols = ["match_id", "season", "date", "team1", "team2", "venue", "winner", "margin_display", "player_of_match"]
        cols = [c for c in display_cols if c in df.columns]
        return df[cols].sort_values(by="match_id", ascending=False).reset_index(drop=True)

    def get_match_scorecard(self, match_id: int) -> Dict:
        match_row = self.df_matches[self.df_matches["match_id"] == match_id]
        if match_row.empty:
            return {"error": f"Match ID {match_id} not found."}

        details = match_row.iloc[0].to_dict()
        res = {"match_info": details}

        if self.df_deliveries is not None:
            deliv = self.df_deliveries[self.df_deliveries["match_id"] == match_id]
            if not deliv.empty:
                innings_list = []
                for inn_num, inn_df in deliv.groupby("inning"):
                    batting_team = inn_df["batting_team"].iloc[0]
                    bowling_team = inn_df["bowling_team"].iloc[0]
                    total_runs = int(inn_df["total_runs"].sum())
                    total_wickets = int(inn_df["is_bowler_wicket"].sum()) if "is_bowler_wicket" in inn_df.columns else int(inn_df["is_wicket"].sum())
                    legal_balls = int(((inn_df["wide_runs"] == 0) & (inn_df["noball_runs"] == 0)).sum())
                    overs_str = balls_to_overs_str(legal_balls)

                    # Top Batsmen in this innings
                    batsman_runs = inn_df.groupby("batsman")["batsman_runs"].sum().sort_values(ascending=False)
                    top_batsmen = [{"batsman": b, "runs": int(r)} for b, r in batsman_runs.head(3).items()]

                    # Top Bowlers in this innings
                    bowler_stats = inn_df.groupby("bowler").agg(
                        wickets=("is_bowler_wicket", "sum"),
                        runs=("total_runs", "sum")
                    ).sort_values(by=["wickets", "runs"], ascending=[False, True])
                    top_bowlers = [{"bowler": b, "wickets": int(row["wickets"]), "runs": int(row["runs"])} for b, row in bowler_stats.head(3).iterrows()]

                    innings_list.append({
                        "inning": inn_num,
                        "batting_team": batting_team,
                        "bowling_team": bowling_team,
                        "total_runs": total_runs,
                        "total_wickets": total_wickets,
                        "overs": overs_str,
                        "top_batsmen": top_batsmen,
                        "top_bowlers": top_bowlers
                    })
                res["innings"] = innings_list

                # Over-by-over worm data
                worm_data = []
                for inn_num, inn_df in deliv.groupby("inning"):
                    over_prog = inn_df.groupby("over")["total_runs"].sum().cumsum().reset_index()
                    over_prog.columns = ["over", "cumulative_runs"]
                    over_prog["inning"] = inn_num
                    over_prog["team"] = inn_df["batting_team"].iloc[0]
                    worm_data.extend(over_prog.to_dict(orient="records"))
                res["worm_progression"] = worm_data

        return res

    def get_margin_distribution(self) -> Dict:
        df = self.df_matches
        runs_margins = df[df["win_by_runs"] > 0]["win_by_runs"].tolist()
        wickets_margins = df[df["win_by_wickets"] > 0]["win_by_wickets"].tolist()
        
        return {
            "win_by_runs": {
                "count": len(runs_margins),
                "mean": round(float(np.mean(runs_margins)), 1) if runs_margins else 0.0,
                "median": float(np.median(runs_margins)) if runs_margins else 0.0,
                "max": int(max(runs_margins)) if runs_margins else 0,
                "values": runs_margins
            },
            "win_by_wickets": {
                "count": len(wickets_margins),
                "mean": round(float(np.mean(wickets_margins)), 1) if wickets_margins else 0.0,
                "median": float(np.median(wickets_margins)) if wickets_margins else 0.0,
                "max": int(max(wickets_margins)) if wickets_margins else 0,
                "values": wickets_margins
            }
        }

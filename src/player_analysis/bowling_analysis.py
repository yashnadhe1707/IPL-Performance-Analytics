"""
Bowling Performance Analytics.
Calculates bowling metrics including wickets, overs, economy rate,
bowling average, bowling strike rate, and best bowling figures.
"""

from typing import Dict, List, Optional
import pandas as pd
import numpy as np
from src.utils.helpers import (
    safe_divide,
    balls_to_overs_str,
    balls_to_decimal_overs
)

class BowlingAnalysis:
    def __init__(self, df_deliveries: pd.DataFrame, df_matches: Optional[pd.DataFrame] = None):
        self.df_deliveries = df_deliveries.copy()
        self.df_matches = df_matches.copy() if df_matches is not None else None

    def _filter_data(self, season: Optional[str] = None, team: Optional[str] = None) -> pd.DataFrame:
        df = self.df_deliveries
        if season is not None and "season" in df.columns:
            df = df[df["season"].astype(str) == str(season)]
        if team is not None and "bowling_team" in df.columns:
            df = df[df["bowling_team"] == team]
        return df

    def get_all_bowlers_summary(self, season: Optional[str] = None, team: Optional[str] = None, min_overs: int = 0) -> pd.DataFrame:
        df = self._filter_data(season=season, team=team)
        if df.empty:
            return pd.DataFrame()

        df["is_legal_ball"] = ((df["wide_runs"] == 0) & (df["noball_runs"] == 0)).astype(int)
        df["bowler_runs_conceded"] = df["batsman_runs"] + df["wide_runs"] + df["noball_runs"]

        if "is_bowler_wicket" not in df.columns:
            df["is_bowler_wicket"] = df["is_wicket"]

        legal_balls_s = df.groupby("bowler")["is_legal_ball"].sum()
        runs_s = df.groupby("bowler")["bowler_runs_conceded"].sum()
        wickets_s = df.groupby("bowler")["is_bowler_wicket"].sum()
        dots_s = df[(df["is_legal_ball"] == 1) & (df["batsman_runs"] == 0)].groupby("bowler")["is_legal_ball"].count()
        innings_s = df.groupby("bowler")["match_id"].nunique()

        inn_grp = df.groupby(["bowler", "match_id", "inning"]).agg(
            inn_wickets=("is_bowler_wicket", "sum"),
            inn_runs=("bowler_runs_conceded", "sum")
        ).reset_index()

        best_fig_dict = {}
        three_w_dict = {}
        four_w_dict = {}
        five_w_dict = {}

        for bowler, b_df in inn_grp.groupby("bowler"):
            three_w_dict[bowler] = int((b_df["inn_wickets"] >= 3).sum())
            four_w_dict[bowler] = int((b_df["inn_wickets"] >= 4).sum())
            five_w_dict[bowler] = int((b_df["inn_wickets"] >= 5).sum())

            sorted_inn = b_df.sort_values(by=["inn_wickets", "inn_runs"], ascending=[False, True])
            best_row = sorted_inn.iloc[0]
            best_fig_dict[bowler] = f"{int(best_row['inn_wickets'])}/{int(best_row['inn_runs'])}"

        all_bowlers = legal_balls_s.index
        records = []

        for b in all_bowlers:
            balls = int(legal_balls_s.get(b, 0))
            dec_overs = balls_to_decimal_overs(balls)
            if dec_overs < min_overs:
                continue

            runs = int(runs_s.get(b, 0))
            wickets = int(wickets_s.get(b, 0))
            dots = int(dots_s.get(b, 0))
            innings = int(innings_s.get(b, 0))

            econ = safe_divide(runs, dec_overs, default=0.0)
            avg = safe_divide(runs, wickets, default=0.0) if wickets > 0 else np.nan
            sr = safe_divide(balls, wickets, default=0.0) if wickets > 0 else np.nan
            dot_pct = safe_divide(dots * 100, balls, default=0.0)

            records.append({
                "Bowler": b,
                "Innings": innings,
                "Overs": balls_to_overs_str(balls),
                "Balls": balls,
                "Runs Conceded": runs,
                "Wickets": wickets,
                "Economy": econ,
                "Average": avg,
                "Strike Rate": sr,
                "Best Bowling": best_fig_dict.get(b, "0/0"),
                "Dot %": dot_pct,
                "3+ Wickets": three_w_dict.get(b, 0),
                "4+ Wickets": four_w_dict.get(b, 0),
                "5+ Wickets": five_w_dict.get(b, 0)
            })

        res_df = pd.DataFrame(records)
        if not res_df.empty:
            res_df = res_df.sort_values(by=["Wickets", "Economy"], ascending=[False, True]).reset_index(drop=True)
        return res_df

    def get_bowler_profile(self, bowler_name: str) -> Dict:
        df = self.df_deliveries[self.df_deliveries["bowler"] == bowler_name]
        if df.empty:
            return {"error": f"No bowling records found for {bowler_name}"}

        summary = self.get_all_bowlers_summary()
        b_row = summary[summary["Bowler"] == bowler_name]
        stat_dict = b_row.iloc[0].to_dict() if not b_row.empty else {}

        if "season" in df.columns:
            season_df = df.groupby("season").agg(
                wickets=("is_bowler_wicket", "sum"),
                runs=("batsman_runs", "sum"),
                balls=("ball", "count")
            ).reset_index()
            season_df["Economy"] = season_df.apply(
                lambda r: safe_divide(r["runs"], balls_to_decimal_overs(r["balls"])), axis=1
            )
            stat_dict["season_trends"] = season_df.to_dict(orient="records")

        return stat_dict

"""
Batting Performance Analytics.
Calculates historical batting metrics including runs, averages, strike rates,
milestones (50s, 100s), boundary percentages, and phase-wise splits.
"""

from typing import Dict, List, Optional
import pandas as pd
import numpy as np
from src.utils.helpers import safe_divide

class BattingAnalysis:
    def __init__(self, df_deliveries: pd.DataFrame, df_matches: Optional[pd.DataFrame] = None):
        self.df_deliveries = df_deliveries.copy()
        self.df_matches = df_matches.copy() if df_matches is not None else None

    def _filter_data(self, season: Optional[str] = None, team: Optional[str] = None) -> pd.DataFrame:
        df = self.df_deliveries
        if season is not None and "season" in df.columns:
            df = df[df["season"].astype(str) == str(season)]
        if team is not None and "batting_team" in df.columns:
            df = df[df["batting_team"] == team]
        return df

    def get_all_batsmen_summary(self, season: Optional[str] = None, team: Optional[str] = None, min_runs: int = 0) -> pd.DataFrame:
        df = self._filter_data(season=season, team=team)
        if df.empty:
            return pd.DataFrame()

        df_valid_balls = df[df["wide_runs"] == 0]

        runs_series = df.groupby("batsman")["batsman_runs"].sum()
        balls_series = df_valid_balls.groupby("batsman")["ball"].count()
        fours_series = df[df["batsman_runs"] == 4].groupby("batsman")["ball"].count()
        sixes_series = df[df["batsman_runs"] == 6].groupby("batsman")["ball"].count()
        dots_series = df[(df["batsman_runs"] == 0) & (df["wide_runs"] == 0)].groupby("batsman")["ball"].count()
        innings_series = df.groupby("batsman")["match_id"].nunique()
        dismissals_series = df[df["player_dismissed"].notna()].groupby("player_dismissed")["ball"].count()

        inn_scores = df.groupby(["batsman", "match_id", "inning"])["batsman_runs"].sum().reset_index()
        
        dismissed_combos = set(
            zip(df[df["player_dismissed"].notna()]["match_id"],
                df[df["player_dismissed"].notna()]["inning"],
                df[df["player_dismissed"].notna()]["player_dismissed"])
        )

        fifties_dict = {}
        hundreds_dict = {}
        high_score_dict = {}

        for batsman, grp in inn_scores.groupby("batsman"):
            fifties = 0
            hundreds = 0
            max_score = 0
            is_max_not_out = False

            for _, row in grp.iterrows():
                r = int(row["batsman_runs"])
                m_id = row["match_id"]
                inn = row["inning"]
                was_dismissed = (m_id, inn, batsman) in dismissed_combos

                if r >= 100:
                    hundreds += 1
                elif r >= 50:
                    fifties += 1

                if r > max_score or (r == max_score and not was_dismissed):
                    max_score = r
                    is_max_not_out = not was_dismissed

            fifties_dict[batsman] = fifties
            hundreds_dict[batsman] = hundreds
            high_score_dict[batsman] = f"{max_score}{'*' if is_max_not_out else ''}"

        all_batsmen = runs_series.index
        records = []
        for b in all_batsmen:
            runs = int(runs_series.get(b, 0))
            if runs < min_runs:
                continue
            balls = int(balls_series.get(b, 0))
            innings = int(innings_series.get(b, 0))
            outs = int(dismissals_series.get(b, 0))
            fours = int(fours_series.get(b, 0))
            sixes = int(sixes_series.get(b, 0))
            dots = int(dots_series.get(b, 0))

            avg = safe_divide(runs, outs, default=float(runs)) if outs > 0 else float(runs)
            sr = safe_divide(runs * 100, balls, default=0.0)
            boundary_runs = (fours * 4) + (sixes * 6)
            boundary_pct = safe_divide(boundary_runs * 100, runs, default=0.0)
            dot_pct = safe_divide(dots * 100, balls, default=0.0)

            records.append({
                "Batsman": b,
                "Innings": innings,
                "Runs": runs,
                "Balls": balls,
                "Dismissals": outs,
                "Average": avg,
                "Strike Rate": sr,
                "Highest Score": high_score_dict.get(b, "0"),
                "Fours": fours,
                "Sixes": sixes,
                "50s": fifties_dict.get(b, 0),
                "100s": hundreds_dict.get(b, 0),
                "Boundary %": boundary_pct,
                "Dot %": dot_pct
            })

        res_df = pd.DataFrame(records)
        if not res_df.empty:
            res_df = res_df.sort_values(by="Runs", ascending=False).reset_index(drop=True)
        return res_df

    def get_player_profile(self, player_name: str) -> Dict:
        df = self.df_deliveries[self.df_deliveries["batsman"] == player_name]
        if df.empty:
            return {"error": f"No batting records found for {player_name}"}

        summary = self.get_all_batsmen_summary()
        player_row = summary[summary["Batsman"] == player_name]
        
        stat_dict = player_row.iloc[0].to_dict() if not player_row.empty else {}

        if "over_phase" in df.columns:
            phase_df = df.groupby("over_phase").agg(
                runs=("batsman_runs", "sum"),
                balls=("ball", "count"),
                fours=("is_four", "sum"),
                sixes=("is_six", "sum")
            ).reset_index()
            phase_df["Strike Rate"] = phase_df.apply(lambda r: safe_divide(r["runs"]*100, r["balls"]), axis=1)
            stat_dict["phase_analysis"] = phase_df.to_dict(orient="records")

        if "season" in df.columns:
            season_df = df.groupby("season").agg(
                runs=("batsman_runs", "sum"),
                balls=("ball", "count"),
                fours=("is_four", "sum"),
                sixes=("is_six", "sum")
            ).reset_index()
            season_df["Strike Rate"] = season_df.apply(lambda r: safe_divide(r["runs"]*100, r["balls"]), axis=1)
            stat_dict["season_trends"] = season_df.to_dict(orient="records")

        return stat_dict

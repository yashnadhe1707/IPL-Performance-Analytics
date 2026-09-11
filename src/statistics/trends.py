"""
Statistical Trends Module.
Analyzes long-term historical trajectories in scoring run rates,
boundary frequencies, toss decisions, and match dynamics across seasons.
"""

from typing import Dict, List, Optional
import pandas as pd
import numpy as np
from src.utils.helpers import safe_divide, balls_to_decimal_overs

class StatisticalTrends:
    def __init__(self, df_matches: pd.DataFrame, df_deliveries: pd.DataFrame):
        self.df_matches = df_matches.copy()
        self.df_deliveries = df_deliveries.copy()

    def get_season_scoring_trends(self) -> pd.DataFrame:
        if "season" not in self.df_deliveries.columns:
            return pd.DataFrame()

        trends = []
        for season, s_deliv in self.df_deliveries.groupby("season"):
            m_count = s_deliv["match_id"].nunique()
            total_runs = int(s_deliv["total_runs"].sum())
            total_balls = len(s_deliv[s_deliv["wide_runs"] == 0])
            dec_overs = balls_to_decimal_overs(total_balls)
            run_rate = safe_divide(total_runs, dec_overs)

            sixes = int((s_deliv["batsman_runs"] == 6).sum())
            fours = int((s_deliv["batsman_runs"] == 4).sum())
            wickets = int(s_deliv["is_wicket"].sum())

            trends.append({
                "Season": str(season),
                "Matches": m_count,
                "Total Runs": total_runs,
                "Tournament Run Rate": run_rate,
                "Runs / Match": safe_divide(total_runs, m_count),
                "Sixes / Match": safe_divide(sixes, m_count),
                "Fours / Match": safe_divide(fours, m_count),
                "Wickets / Match": safe_divide(wickets, m_count)
            })

        res_df = pd.DataFrame(trends)
        if not res_df.empty:
            res_df = res_df.sort_values(by="Season").reset_index(drop=True)
        return res_df

    def get_phase_wise_run_rates(self) -> pd.DataFrame:
        if "over_phase" not in self.df_deliveries.columns or "season" not in self.df_deliveries.columns:
            return pd.DataFrame()

        records = []
        for (season, phase), grp in self.df_deliveries.groupby(["season", "over_phase"]):
            runs = grp["total_runs"].sum()
            balls = len(grp[grp["wide_runs"] == 0])
            dec_overs = balls_to_decimal_overs(balls)
            rr = safe_divide(runs, dec_overs)
            records.append({
                "Season": str(season),
                "Phase": phase,
                "Run Rate": rr
            })

        res_df = pd.DataFrame(records)
        if not res_df.empty:
            res_df = res_df.sort_values(by=["Season", "Phase"]).reset_index(drop=True)
        return res_df

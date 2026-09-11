"""
Toss Analysis Module.
Examines toss decision trends (bat vs field), toss winner vs match winner association,
and season-wise toss behaviors.
Strictly adheres to scientific ethics: correlation is not causation.
"""

from typing import Dict, List, Optional
import pandas as pd
import numpy as np
from src.utils.helpers import safe_divide

class TossAnalysis:
    def __init__(self, df_matches: pd.DataFrame):
        self.df_matches = df_matches.copy()

    def get_toss_decision_distribution(self, season: Optional[str] = None) -> Dict:
        df = self.df_matches
        if season is not None and "season" in df.columns:
            df = df[df["season"].astype(str) == str(season)]

        total_matches = len(df)
        if total_matches == 0:
            return {}

        decisions = df["toss_decision"].str.lower().value_counts()
        field_count = int(decisions.get("field", 0))
        bat_count = int(decisions.get("bat", 0))

        return {
            "total_tosses": total_matches,
            "field_count": field_count,
            "bat_count": bat_count,
            "field_pct": safe_divide(field_count * 100, total_matches),
            "bat_pct": safe_divide(bat_count * 100, total_matches)
        }

    def get_toss_winner_match_winner_association(self, season: Optional[str] = None) -> Dict:
        """
        Calculates empirical co-occurrence of winning toss and winning match.
        Strict disclaimer provided in the output payload.
        """
        df = self.df_matches
        if season is not None and "season" in df.columns:
            df = df[df["season"].astype(str) == str(season)]

        total_valid = len(df[df["winner"].notna() & (df["winner"] != "")])
        if total_valid == 0:
            return {}

        toss_and_match_win = len(df[df["toss_winner"] == df["winner"]])
        toss_win_match_loss = total_valid - toss_and_match_win
        win_pct = safe_divide(toss_and_match_win * 100, total_valid)

        # Breakdown by decision
        field_subset = df[df["toss_decision"].str.lower() == "field"]
        field_toss_match_win = len(field_subset[field_subset["toss_winner"] == field_subset["winner"]])
        field_win_pct = safe_divide(field_toss_match_win * 100, len(field_subset)) if len(field_subset) > 0 else 0.0

        bat_subset = df[df["toss_decision"].str.lower() == "bat"]
        bat_toss_match_win = len(bat_subset[bat_subset["toss_winner"] == bat_subset["winner"]])
        bat_win_pct = safe_divide(bat_toss_match_win * 100, len(bat_subset)) if len(bat_subset) > 0 else 0.0

        return {
            "total_matches": total_valid,
            "toss_winner_won_match": toss_and_match_win,
            "toss_winner_lost_match": toss_win_match_loss,
            "association_percentage": win_pct,
            "chasing_win_pct": field_win_pct,
            "defending_win_pct": bat_win_pct,
            "disclaimer": "Historical data shows an empirical association between toss decisions and match outcomes. Correlation does not imply causation."
        }

    def get_season_wise_toss_trend(self) -> pd.DataFrame:
        df = self.df_matches.copy()
        if "season" not in df.columns:
            return pd.DataFrame()

        records = []
        for s, s_df in df.groupby("season"):
            tot = len(s_df)
            field_cnt = int((s_df["toss_decision"].str.lower() == "field").sum())
            bat_cnt = int((s_df["toss_decision"].str.lower() == "bat").sum())
            toss_match_win = int((s_df["toss_winner"] == s_df["winner"]).sum())

            records.append({
                "Season": str(s),
                "Total Matches": tot,
                "Field First": field_cnt,
                "Bat First": bat_cnt,
                "Field %": safe_divide(field_cnt * 100, tot),
                "Toss & Match Win %": safe_divide(toss_match_win * 100, tot)
            })

        res_df = pd.DataFrame(records)
        if not res_df.empty:
            res_df = res_df.sort_values(by="Season").reset_index(drop=True)
        return res_df

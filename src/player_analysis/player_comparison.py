"""
Player Comparison Module.
Enables side-by-side analytical benchmarking of multiple batsmen and bowlers,
including comparative metrics and normalized ranking radar indicators.
"""

from typing import List, Dict, Optional
import pandas as pd
import numpy as np
from src.player_analysis.batting_analysis import BattingAnalysis
from src.player_analysis.bowling_analysis import BowlingAnalysis

class PlayerComparison:
    def __init__(self, df_deliveries: pd.DataFrame, df_matches: Optional[pd.DataFrame] = None):
        self.batting_engine = BattingAnalysis(df_deliveries, df_matches)
        self.bowling_engine = BowlingAnalysis(df_deliveries, df_matches)

    def compare_batsmen(self, player_names: List[str]) -> pd.DataFrame:
        all_batting = self.batting_engine.get_all_batsmen_summary()
        if all_batting.empty:
            return pd.DataFrame()
        matched = all_batting[all_batting["Batsman"].isin(player_names)].copy()
        return matched.reset_index(drop=True)

    def compare_bowlers(self, player_names: List[str]) -> pd.DataFrame:
        all_bowling = self.bowling_engine.get_all_bowlers_summary()
        if all_bowling.empty:
            return pd.DataFrame()
        matched = all_bowling[all_bowling["Bowler"].isin(player_names)].copy()
        return matched.reset_index(drop=True)

    def get_comparison_radar_data(self, player_names: List[str], role: str = "batting") -> List[Dict]:
        if role == "batting":
            df = self.compare_batsmen(player_names)
            if df.empty:
                return []
            metrics = ["Runs", "Average", "Strike Rate", "Fours", "Sixes", "Boundary %"]
            
            all_df = self.batting_engine.get_all_batsmen_summary()
            radar_data = []
            for _, row in df.iterrows():
                p_scores = {"Player": row["Batsman"]}
                for m in metrics:
                    max_val = all_df[m].max() if m in all_df.columns else 1
                    val = row.get(m, 0)
                    p_scores[m] = round((val / max_val * 100), 1) if max_val > 0 else 0
                radar_data.append(p_scores)
            return radar_data
        else:
            df = self.compare_bowlers(player_names)
            if df.empty:
                return []
            metrics = ["Wickets", "Dot %", "3+ Wickets"]
            all_df = self.bowling_engine.get_all_bowlers_summary()
            radar_data = []
            for _, row in df.iterrows():
                p_scores = {"Player": row["Bowler"]}
                for m in metrics:
                    max_val = all_df[m].max() if m in all_df.columns else 1
                    val = row.get(m, 0)
                    p_scores[m] = round((val / max_val * 100), 1) if max_val > 0 else 0
                
                econ = row.get("Economy", 8.0)
                p_scores["Economy Rating"] = max(0.0, round(100 - (econ * 8), 1))
                radar_data.append(p_scores)
            return radar_data

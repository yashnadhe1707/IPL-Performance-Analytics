"""
Performance Rankings Engine.
Ranks players and teams according to transparent statistical benchmarks
(Orange Cap, Purple Cap, Strike Rate, Economy, Win Rates).
"""

from typing import Dict, List, Optional
import pandas as pd
import numpy as np
from src.player_analysis.batting_analysis import BattingAnalysis
from src.player_analysis.bowling_analysis import BowlingAnalysis
from src.team_analysis.team_performance import TeamPerformance

class PerformanceRankings:
    def __init__(self, df_matches: pd.DataFrame, df_deliveries: pd.DataFrame):
        self.df_matches = df_matches.copy()
        self.df_deliveries = df_deliveries.copy()
        self.batting = BattingAnalysis(df_deliveries, df_matches)
        self.bowling = BowlingAnalysis(df_deliveries, df_matches)
        self.team_perf = TeamPerformance(df_matches, df_deliveries)

    def get_top_run_scorers(self, top_n: int = 10, season: Optional[str] = None) -> pd.DataFrame:
        df = self.batting.get_all_batsmen_summary(season=season)
        if df.empty:
            return pd.DataFrame()
        cols = ["Batsman", "Innings", "Runs", "Average", "Strike Rate", "Highest Score", "Fours", "Sixes"]
        ranked = df[cols].sort_values(by=["Runs", "Average"], ascending=[False, False]).head(top_n).reset_index(drop=True)
        ranked.index = ranked.index + 1
        ranked.index.name = "Rank"
        return ranked.reset_index()

    def get_top_wicket_takers(self, top_n: int = 10, season: Optional[str] = None) -> pd.DataFrame:
        df = self.bowling.get_all_bowlers_summary(season=season)
        if df.empty:
            return pd.DataFrame()
        cols = ["Bowler", "Innings", "Overs", "Wickets", "Economy", "Average", "Best Bowling", "3+ Wickets"]
        ranked = df[cols].sort_values(by=["Wickets", "Economy"], ascending=[False, True]).head(top_n).reset_index(drop=True)
        ranked.index = ranked.index + 1
        ranked.index.name = "Rank"
        return ranked.reset_index()

    def get_highest_strike_rates(self, min_balls: int = 50, top_n: int = 10, season: Optional[str] = None) -> pd.DataFrame:
        df = self.batting.get_all_batsmen_summary(season=season)
        if df.empty:
            return pd.DataFrame()
        qualified = df[df["Balls"] >= min_balls].copy()
        cols = ["Batsman", "Balls", "Runs", "Strike Rate", "Average", "Sixes", "Boundary %"]
        ranked = qualified[cols].sort_values(by=["Strike Rate", "Runs"], ascending=[False, False]).head(top_n).reset_index(drop=True)
        ranked.index = ranked.index + 1
        ranked.index.name = "Rank"
        return ranked.reset_index()

    def get_best_bowling_economies(self, min_overs: int = 10, top_n: int = 10, season: Optional[str] = None) -> pd.DataFrame:
        df = self.bowling.get_all_bowlers_summary(season=season, min_overs=min_overs)
        if df.empty:
            return pd.DataFrame()
        cols = ["Bowler", "Overs", "Runs Conceded", "Wickets", "Economy", "Average", "Dot %"]
        ranked = df[cols].sort_values(by=["Economy", "Wickets"], ascending=[True, False]).head(top_n).reset_index(drop=True)
        ranked.index = ranked.index + 1
        ranked.index.name = "Rank"
        return ranked.reset_index()

    def get_team_rankings(self, season: Optional[str] = None) -> pd.DataFrame:
        df = self.team_perf.get_all_teams_summary(season=season)
        if df.empty:
            return pd.DataFrame()
        ranked = df.sort_values(by=["Win %", "Wins", "Average Score"], ascending=[False, False, False]).reset_index(drop=True)
        ranked.index = ranked.index + 1
        ranked.index.name = "Rank"
        return ranked.reset_index()

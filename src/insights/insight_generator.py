"""
Data-Driven Insight Generation Engine.
Synthesizes factual, descriptive, data-grounded observations from computed metrics.
Strictly adheres to scientific guidelines: no hard-coded stats, no unsupported
causal declarations.
"""

from typing import Dict, List, Optional
import pandas as pd
from src.player_analysis.batting_analysis import BattingAnalysis
from src.player_analysis.bowling_analysis import BowlingAnalysis
from src.team_analysis.team_performance import TeamPerformance
from src.match_analysis.toss_analysis import TossAnalysis
from src.match_analysis.venue_analysis import VenueAnalysis

class InsightGenerator:
    def __init__(self, df_matches: pd.DataFrame, df_deliveries: pd.DataFrame):
        self.df_matches = df_matches.copy()
        self.df_deliveries = df_deliveries.copy()
        self.batting = BattingAnalysis(df_deliveries, df_matches)
        self.bowling = BowlingAnalysis(df_deliveries, df_matches)
        self.team_perf = TeamPerformance(df_matches, df_deliveries)
        self.toss = TossAnalysis(df_matches)
        self.venue = VenueAnalysis(df_matches, df_deliveries)

    def generate_all_insights(self, season: Optional[str] = None) -> Dict[str, List[str]]:
        return {
            "tournament": self.generate_tournament_insights(season=season),
            "batting": self.generate_batting_insights(season=season),
            "bowling": self.generate_bowling_insights(season=season),
            "teams": self.generate_team_insights(season=season),
            "toss_and_venues": self.generate_toss_and_venue_insights(season=season)
        }

    def generate_tournament_insights(self, season: Optional[str] = None) -> List[str]:
        insights = []
        df_m = self.df_matches
        if season is not None and "season" in df_m.columns:
            df_m = df_m[df_m["season"].astype(str) == str(season)]

        total_matches = len(df_m)
        if total_matches == 0:
            return ["No match records available for the selected parameters."]

        insights.append(
            f"The analyzed dataset includes {total_matches} matches across "
            f"{df_m['venue'].nunique()} venues."
        )

        # Average winning margins
        run_wins = df_m[df_m["win_by_runs"] > 0]["win_by_runs"]
        wkt_wins = df_m[df_m["win_by_wickets"] > 0]["win_by_wickets"]
        if not run_wins.empty:
            insights.append(
                f"Defending teams won by an average margin of {run_wins.mean():.1f} runs "
                f"(maximum victory margin: {int(run_wins.max())} runs)."
            )
        if not wkt_wins.empty:
            insights.append(
                f"Chasing teams won by an average margin of {wkt_wins.mean():.1f} wickets "
                f"(maximum: {int(wkt_wins.max())} wickets)."
            )

        return insights

    def generate_batting_insights(self, season: Optional[str] = None) -> List[str]:
        insights = []
        df_batsmen = self.batting.get_all_batsmen_summary(season=season)
        if df_batsmen.empty:
            return ["Insufficient batting data for the selected filter."]

        top_run = df_batsmen.iloc[0]
        insights.append(
            f"Top Run Scorer: {top_run['Batsman']} accumulated {top_run['Runs']} runs in {top_run['Innings']} innings "
            f"at an average of {top_run['Average']:.2f} and a strike rate of {top_run['Strike Rate']:.2f}."
        )

        # Power hitting insight
        six_hitter = df_batsmen.sort_values(by="Sixes", ascending=False).iloc[0]
        if six_hitter["Sixes"] > 0:
            insights.append(
                f"Power Hitter: {six_hitter['Batsman']} recorded the most sixes ({six_hitter['Sixes']}) with a boundary contribution of {six_hitter['Boundary %']:.1f}%."
            )

        # Milestone insight
        century_makers = df_batsmen[df_batsmen["100s"] > 0]
        if not century_makers.empty:
            tot_100s = int(century_makers["100s"].sum())
            insights.append(
                f"Century Count: A total of {tot_100s} centuries were registered in this dataset."
            )

        return insights

    def generate_bowling_insights(self, season: Optional[str] = None) -> List[str]:
        insights = []
        df_bowlers = self.bowling.get_all_bowlers_summary(season=season)
        if df_bowlers.empty:
            return ["Insufficient bowling data for the selected filter."]

        top_wkt = df_bowlers.iloc[0]
        insights.append(
            f"Leading Wicket Taker: {top_wkt['Bowler']} captured {top_wkt['Wickets']} wickets across {top_wkt['Innings']} innings "
            f"with an economy rate of {top_wkt['Economy']:.2f} and best figures of {top_wkt['Best Bowling']}."
        )

        # Economy leader (min 10 overs)
        econ_qual = df_bowlers[df_bowlers["Balls"] >= 60]
        if not econ_qual.empty:
            best_econ = econ_qual.sort_values(by="Economy").iloc[0]
            insights.append(
                f"Most Economical Bowler: {best_econ['Bowler']} conceded only {best_econ['Economy']:.2f} runs per over "
                f"over {best_econ['Overs']} overs bowled."
            )

        return insights

    def generate_team_insights(self, season: Optional[str] = None) -> List[str]:
        insights = []
        df_teams = self.team_perf.get_all_teams_summary(season=season)
        if df_teams.empty:
            return ["Insufficient team data for the selected filter."]

        top_win = df_teams.iloc[0]
        insights.append(
            f"Highest Win Percentage: {top_win['Team']} registered the highest win rate ({top_win['Win %']:.1f}%), "
            f"securing {top_win['Wins']} wins from {top_win['Matches']} matches."
        )

        if "Average Score" in df_teams.columns and df_teams["Average Score"].max() > 0:
            top_scoring_team = df_teams.sort_values(by="Average Score", ascending=False).iloc[0]
            insights.append(
                f"Highest Average Team Total: {top_scoring_team['Team']} averaged {top_scoring_team['Average Score']:.1f} runs per innings."
            )

        return insights

    def generate_toss_and_venue_insights(self, season: Optional[str] = None) -> List[str]:
        insights = []
        toss_dist = self.toss.get_toss_decision_distribution(season=season)
        if toss_dist:
            insights.append(
                f"Toss Preferences: Teams chose to field first in {toss_dist['field_pct']:.1f}% of matches ({toss_dist['field_count']} of {toss_dist['total_tosses']})."
            )

        toss_assoc = self.toss.get_toss_winner_match_winner_association(season=season)
        if toss_assoc:
            insights.append(
                f"Toss & Match Outcome: The toss winner also won the match in {toss_assoc['association_percentage']:.1f}% of historical games. "
                "Note: Historical data reflects an empirical association; correlation does not imply causation."
            )

        df_venues = self.venue.get_all_venues_summary()
        if not df_venues.empty and "Avg Innings Score" in df_venues.columns:
            top_venue = df_venues.sort_values(by="Avg Innings Score", ascending=False).iloc[0]
            insights.append(
                f"High-Scoring Ground: {top_venue['Venue']} recorded the highest average innings score ({top_venue['Avg Innings Score']:.1f} runs)."
            )

        return insights

"""
Data Cleaner and Feature Engineering module for IPL Performance Analytics.
Cleans raw match and delivery datasets, normalizes team/player names,
handles missing data gracefully, and creates analytical cricket features.
"""

from typing import Optional, Tuple
import pandas as pd
import numpy as np
from src.utils.helpers import (
    standardize_team_name,
    standardize_player_name
)

# Standard Column Name Mapping for Matches
MATCHES_COLUMN_MAPPING = {
    "id": "match_id",
    "match_id": "match_id",
    "season": "season",
    "city": "city",
    "date": "date",
    "team1": "team1",
    "team2": "team2",
    "toss_winner": "toss_winner",
    "toss_decision": "toss_decision",
    "result": "result",
    "dl_applied": "dl_applied",
    "winner": "winner",
    "win_by_runs": "win_by_runs",
    "win_by_wickets": "win_by_wickets",
    "player_of_match": "player_of_match",
    "venue": "venue",
    "umpire1": "umpire1",
    "umpire2": "umpire2"
}

# Standard Column Name Mapping for Deliveries
DELIVERIES_COLUMN_MAPPING = {
    "match_id": "match_id",
    "inning": "inning",
    "batting_team": "batting_team",
    "bowling_team": "bowling_team",
    "over": "over",
    "ball": "ball",
    "batter": "batsman",
    "batsman": "batsman",
    "non_striker": "non_striker",
    "bowler": "bowler",
    "is_super_over": "is_super_over",
    "wide_runs": "wide_runs",
    "bye_runs": "bye_runs",
    "legbye_runs": "legbye_runs",
    "noball_runs": "noball_runs",
    "penalty_runs": "penalty_runs",
    "batsman_runs": "batsman_runs",
    "extra_runs": "extra_runs",
    "total_runs": "total_runs",
    "player_dismissed": "player_dismissed",
    "dismissal_kind": "dismissal_kind",
    "fielder": "fielder",
    "is_wicket": "is_wicket"
}

class IPLCleaner:
    def __init__(self, map_franchise_history: bool = True):
        self.map_franchise_history = map_franchise_history

    def clean_matches(self, df_matches: pd.DataFrame) -> pd.DataFrame:
        df = df_matches.copy()
        
        # 1. Rename columns to standard schema
        rename_dict = {}
        for col in df.columns:
            cleaned_col = col.strip().lower().replace(" ", "_")
            if cleaned_col in MATCHES_COLUMN_MAPPING:
                rename_dict[col] = MATCHES_COLUMN_MAPPING[cleaned_col]
        df = df.rename(columns=rename_dict)

        # 2. Ensure critical columns exist
        if "match_id" not in df.columns and "id" in df.columns:
            df["match_id"] = df["id"]

        # Drop duplicate match entries
        df = df.drop_duplicates(subset=["match_id"]).copy()

        # 3. Standardize dates and season
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"], errors="coerce")
            if "season" not in df.columns or df["season"].isna().all():
                df["season"] = df["date"].dt.year
        
        # Ensure season is string format (e.g. '2023')
        if "season" in df.columns:
            df["season"] = df["season"].astype(str).str.split("/").str[0].str.strip()

        # 4. Standardize Team Names
        team_cols = ["team1", "team2", "toss_winner", "winner"]
        for col in team_cols:
            if col in df.columns:
                df[col] = df[col].apply(lambda x: standardize_team_name(x, self.map_franchise_history))

        # 5. Clean Player of Match
        if "player_of_match" in df.columns:
            df["player_of_match"] = df["player_of_match"].fillna("None Awarded").apply(standardize_player_name)

        # 6. Clean Venue & City
        if "venue" in df.columns:
            df["venue"] = df["venue"].fillna("Unknown Venue").str.strip()
        if "city" in df.columns:
            df["city"] = df["city"].fillna("Unknown City").str.strip()

        # 7. Margins and Result
        for num_col in ["win_by_runs", "win_by_wickets"]:
            if num_col in df.columns:
                df[num_col] = pd.to_numeric(df[num_col], errors="coerce").fillna(0).astype(int)

        if "toss_decision" in df.columns:
            df["toss_decision"] = df["toss_decision"].str.lower().str.strip()

        # Derived margin text
        def format_margin(row):
            if row.get("win_by_runs", 0) > 0:
                return f"{row['win_by_runs']} runs"
            elif row.get("win_by_wickets", 0) > 0:
                return f"{row['win_by_wickets']} wickets"
            elif row.get("result") in ["tie", "super over"]:
                return "Super Over"
            return "No Result / Normal"

        df["margin_display"] = df.apply(format_margin, axis=1)

        return df

    def clean_deliveries(self, df_deliveries: pd.DataFrame, df_matches: Optional[pd.DataFrame] = None) -> pd.DataFrame:
        df = df_deliveries.copy()

        # 1. Rename columns
        rename_dict = {}
        for col in df.columns:
            cleaned_col = col.strip().lower().replace(" ", "_")
            if cleaned_col in DELIVERIES_COLUMN_MAPPING:
                rename_dict[col] = DELIVERIES_COLUMN_MAPPING[cleaned_col]
        df = df.rename(columns=rename_dict)

        # 2. Standardize Team Names
        for col in ["batting_team", "bowling_team"]:
            if col in df.columns:
                df[col] = df[col].apply(lambda x: standardize_team_name(x, self.map_franchise_history))

        # 3. Standardize Player Names
        for col in ["batsman", "non_striker", "bowler", "player_dismissed", "fielder"]:
            if col in df.columns:
                df[col] = df[col].apply(lambda x: standardize_player_name(x) if pd.notna(x) else np.nan)

        # 4. Fill numeric runs
        for col in ["batsman_runs", "extra_runs", "total_runs", "wide_runs", "bye_runs", "legbye_runs", "noball_runs"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

        if "total_runs" not in df.columns and "batsman_runs" in df.columns and "extra_runs" in df.columns:
            df["total_runs"] = df["batsman_runs"] + df["extra_runs"]

        # 5. Over numbering standard (0-19 vs 1-20 check)
        if "over" in df.columns:
            # If overs are 0-indexed (0 to 19), convert to 1-20
            if df["over"].min() == 0:
                df["over"] = df["over"] + 1

        # 6. Feature Engineering
        df["is_dot"] = ((df["batsman_runs"] == 0) & (df["extra_runs"] == 0)).astype(int)
        df["is_four"] = (df["batsman_runs"] == 4).astype(int)
        df["is_six"] = (df["batsman_runs"] == 6).astype(int)
        df["is_boundary"] = (df["batsman_runs"].isin([4, 6])).astype(int)

        # Wickets credited to bowlers (excludes run out, retired hurt/out)
        non_bowler_dismissals = ["run out", "retired hurt", "retired out", "obstructing the field"]
        if "is_wicket" in df.columns:
            df["is_wicket"] = pd.to_numeric(df["is_wicket"], errors="coerce").fillna(0).astype(int)
        else:
            df["is_wicket"] = df["player_dismissed"].notna().astype(int)

        if "dismissal_kind" in df.columns:
            df["dismissal_kind"] = df["dismissal_kind"].astype(str).str.lower().str.strip()
            df["is_bowler_wicket"] = (
                (df["is_wicket"] == 1) & 
                (~df["dismissal_kind"].isin(non_bowler_dismissals)) &
                (df["dismissal_kind"] != "nan")
            ).astype(int)
        else:
            df["is_bowler_wicket"] = df["is_wicket"]

        # Phase of match
        def get_phase(over_num):
            if over_num <= 6:
                return "Powerplay"
            elif over_num <= 15:
                return "Middle"
            return "Death"

        if "over" in df.columns:
            df["over_phase"] = df["over"].apply(get_phase)

        # Merge season and date from matches if available
        if df_matches is not None and "match_id" in df.columns and "match_id" in df_matches.columns:
            match_subset = df_matches[["match_id", "season", "date", "venue"]].drop_duplicates(subset=["match_id"])
            df = df.merge(match_subset, on="match_id", how="left")

        return df

    def clean_pipeline(self, df_matches: pd.DataFrame, df_deliveries: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
        cleaned_matches = self.clean_matches(df_matches)
        cleaned_deliveries = self.clean_deliveries(df_deliveries, cleaned_matches)
        return cleaned_matches, cleaned_deliveries

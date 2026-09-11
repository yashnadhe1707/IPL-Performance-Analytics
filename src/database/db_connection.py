"""
SQLite Database Connection and Initialization Module.
Provides lightweight local database operations and migration of processed datasets.
"""

import os
import sqlite3
from typing import Optional
import pandas as pd

class IPLDatabase:
    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
            self.db_path = os.path.join(base_dir, "database", "ipl.db")
            self.schema_path = os.path.join(base_dir, "database", "schema.sql")
        else:
            self.db_path = os.path.abspath(db_path)
            self.schema_path = os.path.join(os.path.dirname(self.db_path), "schema.sql")

    def get_connection(self) -> sqlite3.Connection:
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_database(self) -> None:
        if not os.path.exists(self.schema_path):
            raise FileNotFoundError(f"Schema file not found at {self.schema_path}")
        with open(self.schema_path, "r", encoding="utf-8") as f:
            schema_script = f.read()

        with self.get_connection() as conn:
            conn.executescript(schema_script)
            conn.commit()
        print("SQLite Database initialized successfully.")

    def populate_from_dataframes(self, df_matches: pd.DataFrame, df_deliveries: pd.DataFrame) -> None:
        self.init_database()
        conn = self.get_connection()

        # 1. Insert Teams
        teams = sorted(list(set(df_matches["team1"].dropna().unique()).union(set(df_matches["team2"].dropna().unique()))))
        with conn:
            conn.executemany(
                "INSERT OR IGNORE INTO teams (team_name) VALUES (?)",
                [(t,) for t in teams]
            )

        # 2. Insert Players
        players = sorted(list(set(df_deliveries["batsman"].dropna().unique()).union(set(df_deliveries["bowler"].dropna().unique()))))
        with conn:
            conn.executemany(
                "INSERT OR IGNORE INTO players (player_name) VALUES (?)",
                [(p,) for p in players]
            )

        # 3. Insert Matches
        matches_records = []
        for _, r in df_matches.iterrows():
            matches_records.append((
                int(r["match_id"]),
                str(r.get("season", "")),
                str(r.get("date", "")),
                str(r.get("venue", "")),
                str(r.get("city", "")),
                str(r.get("team1", "")),
                str(r.get("team2", "")),
                str(r.get("toss_winner", "")),
                str(r.get("toss_decision", "")),
                str(r.get("winner", "")),
                str(r.get("result", "")),
                int(r.get("win_by_runs", 0)),
                int(r.get("win_by_wickets", 0)),
                str(r.get("player_of_match", ""))
            ))
        with conn:
            conn.executemany(
                """INSERT OR REPLACE INTO matches 
                (match_id, season, date, venue, city, team1, team2, toss_winner, toss_decision, winner, result, win_by_runs, win_by_wickets, player_of_match)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                matches_records
            )

        conn.close()
        print("Matches and rosters successfully loaded into SQLite database.")

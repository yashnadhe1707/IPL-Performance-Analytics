"""
Database Query Service.
Provides parameterized SQL queries to retrieve matches, teams, and tournament stats.
"""

from typing import List, Dict, Optional
import pandas as pd
from src.database.db_connection import IPLDatabase

class IPLQueries:
    def __init__(self, db: Optional[IPLDatabase] = None):
        self.db = db if db is not None else IPLDatabase()

    def get_all_matches(self, season: Optional[str] = None) -> pd.DataFrame:
        conn = self.db.get_connection()
        if season is not None:
            query = "SELECT * FROM matches WHERE season = ? ORDER BY date DESC"
            df = pd.read_sql_query(query, conn, params=(str(season),))
        else:
            query = "SELECT * FROM matches ORDER BY date DESC"
            df = pd.read_sql_query(query, conn)
        conn.close()
        return df

    def get_team_wins_summary(self) -> pd.DataFrame:
        conn = self.db.get_connection()
        query = """
        SELECT winner AS team, COUNT(*) as wins
        FROM matches
        WHERE winner IS NOT NULL AND winner != ''
        GROUP BY winner
        ORDER BY wins DESC;
        """
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df

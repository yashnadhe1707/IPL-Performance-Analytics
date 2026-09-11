"""
Data Loader module for IPL Performance Analytics.
Discovers, validates, and loads historical IPL datasets (matches and deliveries)
from the data/raw directory or starter dataset generator.
"""

import os
from typing import Dict, Optional, Tuple
import pandas as pd

class IPLDataLoader:
    def __init__(self, base_dir: Optional[str] = None):
        if base_dir is None:
            # Default to project root
            self.base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        else:
            self.base_dir = os.path.abspath(base_dir)
        self.raw_dir = os.path.join(self.base_dir, "data", "raw")
        self.processed_dir = os.path.join(self.base_dir, "data", "processed")

    def find_file(self, possible_names: list[str]) -> Optional[str]:
        if not os.path.exists(self.raw_dir):
            return None
        available_files = {f.lower(): f for f in os.listdir(self.raw_dir)}
        for name in possible_names:
            if name.lower() in available_files:
                return os.path.join(self.raw_dir, available_files[name.lower()])
        return None

    def get_matches_path(self) -> Optional[str]:
        return self.find_file([
            "matches.csv",
            "ipl_matches.csv",
            "IPL_Matches.csv",
            "Match.csv",
            "matches_data.csv"
        ])

    def get_deliveries_path(self) -> Optional[str]:
        return self.find_file([
            "deliveries.csv",
            "ipl_deliveries.csv",
            "IPL_Deliveries.csv",
            "Deliveries.csv",
            "ball_by_ball.csv",
            "deliveries_data.csv"
        ])

    def raw_data_exists(self) -> bool:
        return bool(self.get_matches_path() and self.get_deliveries_path())

    def load_raw_data(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Loads raw matches and deliveries dataframes.
        Raises FileNotFoundError with instructions if files are missing.
        """
        matches_path = self.get_matches_path()
        deliveries_path = self.get_deliveries_path()

        if not matches_path or not deliveries_path:
            missing = []
            if not matches_path:
                missing.append("matches.csv")
            if not deliveries_path:
                missing.append("deliveries.csv")
            err_msg = (
                f"Missing required raw dataset file(s): {', '.join(missing)} in '{self.raw_dir}'. "
                "Please place the official IPL datasets in 'data/raw/' or generate the starter dataset."
            )
            raise FileNotFoundError(err_msg)

        df_matches = pd.read_csv(matches_path, low_memory=False)
        df_deliveries = pd.read_csv(deliveries_path, low_memory=False)
        return df_matches, df_deliveries

    def load_processed_data(self) -> Tuple[Optional[pd.DataFrame], Optional[pd.DataFrame]]:
        """Loads clean processed files if they exist."""
        clean_matches_path = os.path.join(self.processed_dir, "clean_matches.csv")
        clean_deliveries_path = os.path.join(self.processed_dir, "clean_deliveries.csv")

        df_matches = pd.read_csv(clean_matches_path, low_memory=False) if os.path.exists(clean_matches_path) else None
        df_deliveries = pd.read_csv(clean_deliveries_path, low_memory=False) if os.path.exists(clean_deliveries_path) else None
        return df_matches, df_deliveries

    def save_processed_data(self, df_matches: pd.DataFrame, df_deliveries: pd.DataFrame) -> None:
        os.makedirs(self.processed_dir, exist_ok=True)
        df_matches.to_csv(os.path.join(self.processed_dir, "clean_matches.csv"), index=False)
        df_deliveries.to_csv(os.path.join(self.processed_dir, "clean_deliveries.csv"), index=False)
        print("Processed datasets successfully saved to data/processed/")

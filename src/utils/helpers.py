"""
Helper utilities for IPL Performance Analytics.
Provides safe division, cricket overs conversions, IPL team color mappings,
and name standardization routines.
"""

from typing import Any, Dict, Optional, Union
import numpy as np
import pandas as pd

TEAM_NAME_MAPPING = {
    "Delhi Daredevils": "Delhi Capitals",
    "Kings XI Punjab": "Punjab Kings",
    "Rising Pune Supergiants": "Rising Pune Supergiant",
    "Royal Challengers Bangalore": "Royal Challengers Bengaluru",
    "Deccan Chargers": "Sunrisers Hyderabad",
}

TEAM_COLORS = {
    "Chennai Super Kings": "#F9CD05",
    "Mumbai Indians": "#004BA0",
    "Royal Challengers Bengaluru": "#D32F2F",
    "Royal Challengers Bangalore": "#D32F2F",
    "Kolkata Knight Riders": "#3A225D",
    "Delhi Capitals": "#0078BC",
    "Delhi Daredevils": "#0078BC",
    "Punjab Kings": "#ED1B24",
    "Kings XI Punjab": "#ED1B24",
    "Rajasthan Royals": "#EA1A85",
    "Sunrisers Hyderabad": "#FF822A",
    "Deccan Chargers": "#FF822A",
    "Gujarat Titans": "#1B2133",
    "Lucknow Super Giants": "#38B6FF",
    "Rising Pune Supergiant": "#D11D5B",
    "Rising Pune Supergiants": "#D11D5B",
    "Gujarat Lions": "#E04F16",
    "Pune Warriors": "#2F9BE3",
    "Kochi Tuskers Kerala": "#632B7A",
}

TEAM_SHORT_NAMES = {
    "Chennai Super Kings": "CSK",
    "Mumbai Indians": "MI",
    "Royal Challengers Bengaluru": "RCB",
    "Royal Challengers Bangalore": "RCB",
    "Kolkata Knight Riders": "KKR",
    "Delhi Capitals": "DC",
    "Delhi Daredevils": "DD",
    "Punjab Kings": "PBKS",
    "Kings XI Punjab": "KXIP",
    "Rajasthan Royals": "RR",
    "Sunrisers Hyderabad": "SRH",
    "Deccan Chargers": "DCG",
    "Gujarat Titans": "GT",
    "Lucknow Super Giants": "LSG",
    "Rising Pune Supergiant": "RPS",
    "Rising Pune Supergiants": "RPS",
    "Gujarat Lions": "GL",
    "Pune Warriors": "PWI",
    "Kochi Tuskers Kerala": "KTK",
}


def safe_divide(
    numerator: Union[int, float],
    denominator: Union[int, float],
    default: float = 0.0,
    round_to: Optional[int] = 2,
) -> float:
    """Safely divide two numbers avoiding ZeroDivisionError or NaN."""
    try:
        if denominator is None or pd.isna(denominator) or denominator == 0:
            return float(default)
        if numerator is None or pd.isna(numerator):
            return float(default)
        val = float(numerator) / float(denominator)
        if np.isnan(val) or np.isinf(val):
            return float(default)
        return round(val, round_to) if round_to is not None else val
    except Exception:
        return float(default)


def balls_to_overs_str(balls: int) -> str:
    """Converts total legal balls into standard cricket overs notation string."""
    if balls is None or pd.isna(balls) or balls <= 0:
        return "0.0"
    overs = int(balls) // 6
    remaining_balls = int(balls) % 6
    return f"{overs}.{remaining_balls}"


def balls_to_decimal_overs(balls: int) -> float:
    """Converts total legal balls into decimal overs for math calculations."""
    if balls is None or pd.isna(balls) or balls <= 0:
        return 0.0
    return float(balls) / 6.0


def overs_str_to_balls(overs_val: Union[str, float, int]) -> int:
    """Converts cricket overs notation (e.g. 19.4 or '19.4') into total legal balls."""
    try:
        s = str(overs_val).strip()
        if "." in s:
            parts = s.split(".")
            return int(parts[0]) * 6 + int(parts[1])
        return int(float(s)) * 6
    except Exception:
        return 0


def standardize_team_name(
    team_name: Any, map_franchise_history: bool = True
) -> str:
    """Normalizes team names and optionally maps renamed franchises."""
    if pd.isna(team_name) or team_name is None:
        return "Unknown Team"
    name = str(team_name).strip()
    if map_franchise_history and name in TEAM_NAME_MAPPING:
        return TEAM_NAME_MAPPING[name]
    return name


def standardize_player_name(player_name: Any) -> str:
    """Cleans and standardizes player name strings."""
    if pd.isna(player_name) or player_name is None:
        return "Unknown Player"
    return " ".join(str(player_name).strip().split())


def get_team_color(team_name: str) -> str:
    """Returns official hex color for a team, or a fallback slate gray."""
    std_name = standardize_team_name(team_name)
    return TEAM_COLORS.get(std_name, TEAM_COLORS.get(team_name, "#4A5568"))


def get_team_short_name(team_name: str) -> str:
    """Returns abbreviation for a team."""
    std_name = standardize_team_name(team_name)
    return TEAM_SHORT_NAMES.get(
        std_name, TEAM_SHORT_NAMES.get(team_name, team_name[:4].upper())
    )

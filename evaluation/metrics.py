"""
Evaluation Metrics Helper Module.
Provides standardized calculations for data completeness, uniqueness,
mathematical validity, and analytical consistency.
"""

from typing import Dict, List, Any
import pandas as pd
import numpy as np

def calculate_missingness(df: pd.DataFrame) -> Dict[str, float]:
    """Calculates missing value percentage for each column."""
    if df.empty:
        return {}
    return {col: round(float((df[col].isna().sum() / len(df)) * 100), 2) for col in df.columns}

def calculate_duplicate_rate(df: pd.DataFrame, subset: List[str] = None) -> float:
    """Calculates percentage of duplicate records."""
    if df.empty:
        return 0.0
    duplicates = df.duplicated(subset=subset).sum()
    return round(float((duplicates / len(df)) * 100), 2)

def validate_metric_range(val: float, min_val: float, max_val: float) -> bool:
    """Verifies that a calculated metric falls within mathematically valid bounds."""
    if val is None or np.isnan(val):
        return False
    return min_val <= val <= max_val

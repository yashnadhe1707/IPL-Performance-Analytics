"""
Statistical Calculations Engine.
Computes parametric and non-parametric statistical metrics:
Mean, Median, Standard Deviation, IQR, Percentiles, Skewness, and Correlation.
"""

from typing import Dict, List, Optional, Union
import pandas as pd
import numpy as np
from scipy import stats

def compute_distribution_summary(series: Union[pd.Series, List[float]]) -> Dict:
    """
    Computes complete statistical profile for a numeric series.
    """
    s = pd.Series(series).dropna()
    if s.empty:
        return {}

    mean_val = float(s.mean())
    std_val = float(s.std()) if len(s) > 1 else 0.0
    median_val = float(s.median())
    q25 = float(np.percentile(s, 25))
    q75 = float(np.percentile(s, 75))
    iqr_val = q75 - q25
    min_val = float(s.min())
    max_val = float(s.max())
    skew_val = float(stats.skew(s)) if len(s) > 2 else 0.0

    return {
        "count": int(len(s)),
        "mean": round(mean_val, 2),
        "std": round(std_val, 2),
        "median": round(median_val, 2),
        "q25": round(q25, 2),
        "q75": round(q75, 2),
        "iqr": round(iqr_val, 2),
        "min": round(min_val, 2),
        "max": round(max_val, 2),
        "skewness": round(skew_val, 2)
    }

def compute_correlation_matrix(df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
    """
    Calculates Pearson correlation matrix for selected numeric features.
    """
    valid_cols = [c for c in columns if c in df.columns and pd.api.types.is_numeric_dtype(df[c])]
    if len(valid_cols) < 2:
        return pd.DataFrame()
    return df[valid_cols].corr(method="pearson").round(3)

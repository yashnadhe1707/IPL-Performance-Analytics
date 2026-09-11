"""
Data Quality Evaluation Script.
Evaluates missing-value percentages, duplicate records, data consistency,
and player/team name integrity.
Exports findings to outputs/evaluation_results/data_quality_report.json.
"""

import os
import json
import sys
import pandas as pd

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.preprocessing.data_loader import IPLDataLoader
from src.preprocessing.data_cleaner import IPLCleaner
from evaluation.metrics import calculate_missingness, calculate_duplicate_rate

def run_data_quality_evaluation():
    loader = IPLDataLoader()
    df_matches, df_deliveries = loader.load_raw_data()
    cleaner = IPLCleaner()
    clean_matches, clean_deliveries = cleaner.clean_pipeline(df_matches, df_deliveries)

    matches_missing = calculate_missingness(clean_matches)
    deliveries_missing = calculate_missingness(clean_deliveries)
    
    matches_dup_rate = calculate_duplicate_rate(clean_matches, subset=["match_id"])
    deliveries_dup_rate = calculate_duplicate_rate(clean_deliveries, subset=["match_id", "inning", "over", "ball"])

    # Name validity checks
    unknown_teams = clean_matches["team1"].str.contains("Unknown", case=False).sum() +                     clean_matches["team2"].str.contains("Unknown", case=False).sum()

    report = {
        "dataset_summary": {
            "total_matches": len(clean_matches),
            "total_deliveries": len(clean_deliveries),
            "total_seasons": clean_matches["season"].nunique(),
            "total_teams": clean_matches["team1"].nunique()
        },
        "missing_values": {
            "matches_columns_with_missing": {k: v for k, v in matches_missing.items() if v > 0},
            "deliveries_columns_with_missing": {k: v for k, v in deliveries_missing.items() if v > 0}
        },
        "duplicates": {
            "matches_duplicate_rate_pct": matches_dup_rate,
            "deliveries_duplicate_rate_pct": deliveries_dup_rate
        },
        "data_integrity": {
            "unknown_teams_count": int(unknown_teams),
            "all_match_ids_unique": bool(clean_matches["match_id"].is_unique),
            "date_parsing_success_pct": round(float((clean_matches["date"].notna().sum() / len(clean_matches)) * 100), 2)
        },
        "status": "PASSED" if matches_dup_rate == 0 and unknown_teams == 0 else "WARNINGS"
    }

    out_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "outputs", "evaluation_results"))
    os.makedirs(out_dir, exist_ok=True)
    report_path = os.path.join(out_dir, "data_quality_report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=4)

    print("Data Quality Evaluation Completed Successfully.")
    print(f"Report saved to: {report_path}")
    print(json.dumps(report, indent=2))
    return report

if __name__ == "__main__":
    run_data_quality_evaluation()

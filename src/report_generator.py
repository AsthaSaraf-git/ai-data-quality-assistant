import os
import pandas as pd


def generate_summary_report(result_df):
    summary_df = (
        result_df
        .groupby("table_name")
        .agg(
            total_rules=("rule", "count"),
            passed_rules=("status", lambda x: (x == "PASSED").sum()),
            failed_rules=("status", lambda x: (x == "FAILED").sum())
        )
        .reset_index()
    )

    summary_df["quality_score"] = (
        summary_df["passed_rules"] / summary_df["total_rules"] * 100
    ).round(2)

    return summary_df


def save_reports(result_df, reports_folder):
    os.makedirs(reports_folder, exist_ok=True)

    detail_report_path = os.path.join(reports_folder, "validation_report.csv")
    summary_report_path = os.path.join(reports_folder, "summary_report.csv")

    result_df.to_csv(detail_report_path, index=False)

    summary_df = generate_summary_report(result_df)
    summary_df.to_csv(summary_report_path, index=False)

    return detail_report_path, summary_report_path, summary_df
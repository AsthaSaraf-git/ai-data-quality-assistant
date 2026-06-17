import os
import pandas as pd
from datetime import datetime


def append_run_history(summary_df, reports_folder):
    history_path = os.path.join(reports_folder, "history.csv")

    run_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    history_df = summary_df.copy()
    history_df["run_timestamp"] = run_timestamp

    history_df = history_df[
        [
            "run_timestamp",
            "table_name",
            "total_rules",
            "passed_rules",
            "failed_rules",
            "quality_score"
        ]
    ]

    if os.path.exists(history_path):
        existing_history_df = pd.read_csv(history_path)
        final_history_df = pd.concat(
            [existing_history_df, history_df],
            ignore_index=True
        )
    else:
        final_history_df = history_df

    final_history_df.to_csv(history_path, index=False)

    return history_path
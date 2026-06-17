import pandas as pd
import matplotlib.pyplot as plt


def generate_trend_chart(history_path, output_path):

    history_df = pd.read_csv(history_path)

    history_df["run_timestamp"] = pd.to_datetime(
        history_df["run_timestamp"]
    )

    for table_name in history_df["table_name"].unique():

        table_df = history_df[
            history_df["table_name"] == table_name
        ].copy()

        plt.figure(figsize=(10, 5))

        plt.plot(
            table_df["run_timestamp"],
            table_df["quality_score"],
            marker="o"
        )

        plt.title(
            f"{table_name} Quality Trend"
        )

        plt.xlabel("Run Time")
        plt.ylabel("Quality Score")

        plt.xticks(rotation=45)

        plt.tight_layout()

        plt.savefig(
            f"reports/{table_name}_quality_trend.png"
        )

        plt.close()
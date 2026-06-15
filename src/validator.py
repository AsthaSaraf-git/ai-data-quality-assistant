import os
import pandas as pd

from file_loader import load_data, load_rules, get_rule_files
from rule_engine import apply_rule
from report_generator import save_reports


def validate_table(df, rules):
    validation_results = []

    table_name = rules["table_name"]

    for column, checks in rules["columns"].items():
        if column not in df.columns:
            validation_results.append({
            "table_name": table_name,
            "column": column,
            "rule": "column_exists",
            "status": "FAILED",
            "failed_count": len(df),
            "total_records": len(df),
            "failure_percentage": 100.00,
            "failed_rows": "column missing"
        })
            continue

        for rule, rule_value in checks.items():
            failed_rows = apply_rule(df, column, rule, rule_value)
            status = "PASSED" if len(failed_rows) == 0 else "FAILED"
            total_records = len(df)
            failed_count = len(failed_rows)
            failure_percentage = round((failed_count / total_records) * 100, 2)
            validation_results.append({
                "table_name": table_name,
                "column": column,
                "rule": rule,
                "status": status,
                "failed_count": failed_count,
                "total_records": total_records,
                "failure_percentage": failure_percentage,
                "failed_rows": failed_rows
            })

    return validation_results


def run_validation_for_all_tables(data_folder, rules_folder, reports_folder):
    all_results = []

    rule_files = get_rule_files(rules_folder)

    for rule_file in rule_files:
        rules = load_rules(rule_file)

        table_name = rules["table_name"]
        data_path = os.path.join(data_folder, f"{table_name}.csv")

        print(f"\nProcessing table: {table_name}")

        if not os.path.exists(data_path):
            print(f"Data file missing: {data_path}")
            continue

        df = load_data(data_path)
        table_results = validate_table(df, rules)

        all_results.extend(table_results)

    result_df = pd.DataFrame(all_results)

    print("\nData Quality Validation Report")
    print("--------------------------------")
    print(result_df)

    detail_report_path, summary_report_path, summary_df = save_reports(result_df, reports_folder)

    print("\nQuality Summary")

    print("--------------------------------")

    print(summary_df)

    print(f"\nDetail report saved to {detail_report_path}")

    print(f"Summary report saved to {summary_report_path}")


if __name__ == "__main__":
    run_validation_for_all_tables(
        data_folder="data",
        rules_folder="rules",
        reports_folder="reports"
    )
import pandas as pd
import yaml
import re


def load_rules(rule_path):
    with open(rule_path, "r") as file:
        return yaml.safe_load(file)


def validate_not_null(df, column):
    failures = df[df[column].isnull() | (df[column].astype(str).str.strip() == "")]
    return failures.index.tolist()


def validate_regex(df, column, pattern):
    failures = []

    for index, value in df[column].items():
        if pd.isnull(value) or str(value).strip() == "":
            continue

        if not re.match(pattern, str(value)):
            failures.append(index)

    return failures


def validate_min(df, column, min_value):
    failures = df[pd.to_numeric(df[column], errors="coerce") < min_value]
    return failures.index.tolist()


def validate_max(df, column, max_value):
    failures = df[pd.to_numeric(df[column], errors="coerce") > max_value]
    return failures.index.tolist()


def run_validation(data_path, rule_path):
    df = pd.read_csv(data_path)
    rules = load_rules(rule_path)

    validation_results = []

    for column, checks in rules["columns"].items():
        if column not in df.columns:
            validation_results.append({
                "column": column,
                "rule": "column_exists",
                "status": "FAILED",
                "failed_rows": "column missing"
            })
            continue

        for rule, rule_value in checks.items():
            failed_rows = []

            if rule == "not_null" and rule_value is True:
                failed_rows = validate_not_null(df, column)

            elif rule == "regex":
                failed_rows = validate_regex(df, column, rule_value)

            elif rule == "min":
                failed_rows = validate_min(df, column, rule_value)

            elif rule == "max":
                failed_rows = validate_max(df, column, rule_value)

            status = "PASSED" if len(failed_rows) == 0 else "FAILED"

            validation_results.append({
                "column": column,
                "rule": rule,
                "status": status,
                "failed_rows": failed_rows
            })

    result_df = pd.DataFrame(validation_results)

    print("\nData Quality Validation Report")
    print("--------------------------------")
    print(result_df)

    result_df.to_csv("reports/validation_report.csv", index=False)
    print("\nReport saved to reports/validation_report.csv")


if __name__ == "__main__":
    run_validation(
        data_path="data/customers.csv",
        rule_path="rules/customer_rules.yaml"
    )
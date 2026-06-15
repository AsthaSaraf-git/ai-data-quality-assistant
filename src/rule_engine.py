
import pandas as pd
import re


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


def apply_rule(df, column, rule, rule_value):
    if rule == "not_null" and rule_value is True:
        return validate_not_null(df, column)

    if rule == "regex":
        return validate_regex(df, column, rule_value)

    if rule == "min":
        return validate_min(df, column, rule_value)

    if rule == "max":
        return validate_max(df, column, rule_value)

    return []
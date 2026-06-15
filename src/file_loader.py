import os
import pandas as pd
import yaml


def load_data(data_path):
    return pd.read_csv(data_path)


def load_rules(rule_path):
    with open(rule_path, "r") as file:
        return yaml.safe_load(file)


def get_rule_files(rules_folder):
    rule_files = []

    for file_name in os.listdir(rules_folder):
        if file_name.endswith(".yaml") or file_name.endswith(".yml"):
            rule_files.append(os.path.join(rules_folder, file_name))

    return rule_files
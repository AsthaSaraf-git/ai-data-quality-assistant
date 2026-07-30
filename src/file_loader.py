import os
import numpy as np
import pandas as pd
import yaml
from databricks import sql


def load_data(data_path):
    return pd.read_csv(data_path, keep_default_na=False, na_values=[""])


def load_table_from_databricks(catalog, schema, table_name):
    server_hostname = os.environ["DATABRICKS_SERVER_HOSTNAME"]
    http_path = os.environ["DATABRICKS_HTTP_PATH"]
    access_token = os.environ["DATABRICKS_TOKEN"]

    with sql.connect(
        server_hostname=server_hostname,
        http_path=http_path,
        access_token=access_token,
    ) as connection:
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT * FROM {catalog}.{schema}.{table_name}")
            columns = [col[0] for col in cursor.description]
            df = pd.DataFrame(cursor.fetchall(), columns=columns)
            # pd.read_csv() treats blank fields as NaN by default; match that
            # here so the not_null/accepted_values rules see the same nulls
            # regardless of which source loaded the table.
            return df.replace("", np.nan)


def load_rules(rule_path):
    with open(rule_path, "r") as file:
        return yaml.safe_load(file)


def get_rule_files(rules_folder):
    rule_files = []

    for file_name in os.listdir(rules_folder):
        if file_name.endswith(".yaml") or file_name.endswith(".yml"):
            rule_files.append(os.path.join(rules_folder, file_name))

    return rule_files
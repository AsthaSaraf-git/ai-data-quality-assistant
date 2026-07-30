from dotenv import load_dotenv

from file_loader import load_table_from_databricks

load_dotenv()

for table_name in ("customers", "products"):
    df = load_table_from_databricks("dq_assistant", "bronze", table_name)
    print(f"{table_name}: {len(df)} rows")
    print(df.head(3))
    print()

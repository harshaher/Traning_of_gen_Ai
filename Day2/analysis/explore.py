import json
from pathlib import Path
import pandas as pd
DATA_FILE = Path(__file__).resolve().parents[1] / "data" / "records.json"
with open(DATA_FILE, "r", encoding="utf-8") as file:
    records = json.load(file)
df = pd.DataFrame(records)
print("\n===== ShellSathi Data Analysis =====")
print("\n1. Total Records:")
print(len(df))
print("\n2. Unique Commands:")
print(df["command"].nunique())
print("\n3. Records by Platform:")
print(df["platform"].value_counts())
print("\n4. Most Common Command:")
print(df["command"].value_counts().head(1))
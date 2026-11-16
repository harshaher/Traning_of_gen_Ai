"""
explore.py - Dataset exploration script for ShellSathi records.
Uses pandas to inspect records.json and displays key insights.
"""

import json
from pathlib import Path
import pandas as pd

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "records.json"


def main():
    if not DATA_FILE.exists():
        print(f"Dataset not found at: {DATA_FILE}")
        return

    with open(DATA_FILE, "r", encoding="utf-8") as file:
        records = json.load(file)

    df = pd.DataFrame(records)

    print("\n================ ShellSathi Data Analysis ================")
    print(f"1. Total Command Records: {len(df)}")
    print(f"2. Unique Linux Commands: {df['command'].nunique()}")
    print("\n3. Records per Command:")
    print(df["command"].value_counts())
    print("\n4. Records by Platform:")
    print(df["platform"].value_counts())
    print("==========================================================\n")


if __name__ == "__main__":
    main()

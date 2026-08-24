

import os
import glob
import yaml
import pandas as pd

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)  # scripts/ is one level under project root

DATA_DIR = os.path.join(PROJECT_ROOT, "data")
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "extracted_csv")

os.makedirs(OUTPUT_DIR, exist_ok=True)

symbol_data = {}

yaml_files = glob.glob(os.path.join(DATA_DIR, "*", "*.yaml"))
print(f"Found {len(yaml_files)} YAML files.")

for file_path in yaml_files:
    with open(file_path, "r") as f:
        records = yaml.safe_load(f)

    if not records:
        continue

    for record in records:
        ticker = record.get("Ticker")
        if not ticker:
            continue

        row = {
            "date": record.get("date"),
            "open": record.get("open"),
            "high": record.get("high"),
            "low": record.get("low"),
            "close": record.get("close"),
            "volume": record.get("volume"),
            "month": record.get("month"),
        }

        symbol_data.setdefault(ticker, []).append(row)

print(f"Writing CSVs for {len(symbol_data)} symbols...")

for ticker, rows in symbol_data.items():
    df = pd.DataFrame(rows)
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").reset_index(drop=True)

    out_path = os.path.join(OUTPUT_DIR, f"{ticker}.csv")
    df.to_csv(out_path, index=False)

print(f"Done. {len(symbol_data)} CSV files written to '{OUTPUT_DIR}/'.")
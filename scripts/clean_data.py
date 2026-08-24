

import os
import glob
import pandas as pd

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

INPUT_DIR = os.path.join(PROJECT_ROOT, "extracted_csv")
OUTPUT_PATH = os.path.join(PROJECT_ROOT, "extracted_csv", "master_data.csv")

csv_files = glob.glob(os.path.join(INPUT_DIR, "*.csv"))
print(f"Found {len(csv_files)} symbol CSV files.")

all_dfs = []

for file_path in csv_files:
    symbol = os.path.splitext(os.path.basename(file_path))[0]

    df = pd.read_csv(file_path)
    df["symbol"] = symbol

    # Ensure correct types
    df["date"] = pd.to_datetime(df["date"])
    for col in ["open", "high", "low", "close", "volume"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Sort by date so pct_change works correctly per symbol
    df = df.sort_values("date").reset_index(drop=True)

    # Drop rows with missing close price (can't compute return without it)
    df = df.dropna(subset=["close"])

    # Daily return: (close - prev_close) / prev_close
    df["daily_return"] = df["close"].pct_change()

    all_dfs.append(df)

# Combine all symbols into one master dataframe
master_df = pd.concat(all_dfs, ignore_index=True)
master_df = master_df.sort_values(["symbol", "date"]).reset_index(drop=True)

# Reorder columns nicely
master_df = master_df[
    ["symbol", "date", "open", "high", "low", "close", "volume", "daily_return", "month"]
]

master_df.to_csv(OUTPUT_PATH, index=False)

print(f"Master dataframe shape: {master_df.shape}")
print(f"Saved cleaned master data to: {OUTPUT_PATH}")
print(master_df.head())
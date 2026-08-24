"""
load_to_sql.py
Loads the cleaned master_data.csv into a SQLite database using SQLAlchemy.
Creates a single 'stocks' table that Streamlit and Power BI can both query.
"""

import os
import pandas as pd
from sqlalchemy import create_engine

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

CSV_PATH = os.path.join(PROJECT_ROOT, "processed_data", "master_data.csv")
DB_PATH = os.path.join(PROJECT_ROOT, "nifty50.db")

df = pd.read_csv(CSV_PATH, parse_dates=["date"])
print(f"Loaded {len(df)} rows from {CSV_PATH}")

engine = create_engine(f"sqlite:///{DB_PATH}")

df.to_sql("stocks", con=engine, if_exists="replace", index=False)

print(f"Loaded data into table 'stocks' in database: {DB_PATH}")

with engine.connect() as conn:
    result = conn.exec_driver_sql("SELECT COUNT(*) FROM stocks")
    count = result.fetchone()[0]
    print(f"Row count in 'stocks' table: {count}")

    result = conn.exec_driver_sql("SELECT DISTINCT symbol FROM stocks")
    symbols = [row[0] for row in result.fetchall()]
    print(f"Number of distinct symbols: {len(symbols)}")
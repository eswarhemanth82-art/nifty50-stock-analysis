"""
analysis.py
Reusable analysis functions for the Nifty 50 Stock Performance project.
Both the Streamlit app and any Power BI export can call these functions
so the numbers stay consistent everywhere.

Reads from the SQLite 'stocks' table (loaded by load_to_sql.py).
"""

import os
import pandas as pd
from sqlalchemy import create_engine

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

DB_PATH = os.path.join(PROJECT_ROOT, "nifty50.db")

SECTOR_CANDIDATES = [
    os.path.join(PROJECT_ROOT, "sector_mapping.csv"),
    os.path.join(PROJECT_ROOT, "sector_data", "sector_mapping.csv"),
    os.path.join(PROJECT_ROOT, "data", "sector_mapping.csv"),
]


def load_stocks_df():
    engine = create_engine(f"sqlite:///{DB_PATH}")
    df = pd.read_sql("SELECT * FROM stocks", con=engine, parse_dates=["date"])
    return df


def load_sector_df():
    for path in SECTOR_CANDIDATES:
        if os.path.exists(path):
            return pd.read_csv(path)
    raise FileNotFoundError(
        "sector_mapping.csv not found. Checked: " + ", ".join(SECTOR_CANDIDATES)
    )


def get_yearly_returns(df):
    rows = []
    for symbol, g in df.groupby("symbol"):
        g = g.sort_values("date")
        first_close = g["close"].iloc[0]
        last_close = g["close"].iloc[-1]
        yearly_return = (last_close - first_close) / first_close
        rows.append({"symbol": symbol, "yearly_return": yearly_return})
    return pd.DataFrame(rows).sort_values("yearly_return", ascending=False).reset_index(drop=True)


def get_top_green_stocks(yearly_returns_df, n=10):
    return yearly_returns_df.sort_values("yearly_return", ascending=False).head(n).reset_index(drop=True)


def get_top_loss_stocks(yearly_returns_df, n=10):
    return yearly_returns_df.sort_values("yearly_return", ascending=True).head(n).reset_index(drop=True)


def get_market_summary(df, yearly_returns_df):
    green_count = (yearly_returns_df["yearly_return"] > 0).sum()
    red_count = (yearly_returns_df["yearly_return"] <= 0).sum()
    avg_price = df["close"].mean()
    avg_volume = df["volume"].mean()
    return {
        "green_stocks": int(green_count),
        "red_stocks": int(red_count),
        "average_price": round(avg_price, 2),
        "average_volume": round(avg_volume, 2),
    }


def get_volatility(df, top_n=10):
    vol = df.groupby("symbol")["daily_return"].std().reset_index()
    vol.columns = ["symbol", "volatility"]
    vol = vol.sort_values("volatility", ascending=False).reset_index(drop=True)
    return vol.head(top_n)


def get_cumulative_returns(df, top_n=5):
    yearly_returns_df = get_yearly_returns(df)
    top_symbols = yearly_returns_df.head(top_n)["symbol"].tolist()

    result = {}
    for symbol in top_symbols:
        g = df[df["symbol"] == symbol].sort_values("date").copy()
        g["cumulative_return"] = (1 + g["daily_return"].fillna(0)).cumprod() - 1
        result[symbol] = g[["date", "cumulative_return"]].reset_index(drop=True)

    return result


def get_sector_performance(df, sector_df):
    yearly_returns_df = get_yearly_returns(df)
    merged = yearly_returns_df.merge(sector_df, on="symbol", how="left")
    sector_perf = merged.groupby("sector")["yearly_return"].mean().reset_index()
    sector_perf.columns = ["sector", "avg_yearly_return"]
    sector_perf = sector_perf.sort_values("avg_yearly_return", ascending=False).reset_index(drop=True)
    return sector_perf, merged


def get_correlation_matrix(df):
    pivot = df.pivot_table(index="date", columns="symbol", values="close")
    corr = pivot.corr()
    return corr


def get_monthly_gainers_losers(df, top_n=5):
    results = {}
    for month, g in df.groupby("month"):
        rows = []
        for symbol, sg in g.groupby("symbol"):
            sg = sg.sort_values("date")
            if len(sg) < 2:
                continue
            first_close = sg["close"].iloc[0]
            last_close = sg["close"].iloc[-1]
            monthly_return = (last_close - first_close) / first_close
            rows.append({"symbol": symbol, "monthly_return": monthly_return})

        month_df = pd.DataFrame(rows).sort_values("monthly_return", ascending=False)
        gainers = month_df.head(top_n).reset_index(drop=True)
        losers = month_df.tail(top_n).sort_values("monthly_return").reset_index(drop=True)
        results[month] = {"gainers": gainers, "losers": losers}

    return results


if __name__ == "__main__":
    df = load_stocks_df()
    print(f"Loaded {len(df)} rows, {df['symbol'].nunique()} symbols")

    yearly_returns_df = get_yearly_returns(df)
    print("\nTop 10 Green Stocks:")
    print(get_top_green_stocks(yearly_returns_df))

    print("\nTop 10 Loss Stocks:")
    print(get_top_loss_stocks(yearly_returns_df))

    print("\nMarket Summary:")
    print(get_market_summary(df, yearly_returns_df))

    print("\nTop 10 Volatile Stocks:")
    print(get_volatility(df))

    print("\nSector Performance:")
    try:
        sector_df = load_sector_df()
        sector_perf, merged = get_sector_performance(df, sector_df)
        print(sector_perf)
        unmatched = merged[merged["sector"].isna()]
        if not unmatched.empty:
            print("\nWARNING: symbols with no sector match:")
            print(unmatched[["symbol"]])
    except FileNotFoundError as e:
        print(e)

    print("\nCorrelation matrix shape:", get_correlation_matrix(df).shape)

    print("\nSample month gainers/losers:")
    monthly = get_monthly_gainers_losers(df)
    first_month = list(monthly.keys())[0]
    print(f"Month: {first_month}")
    print("Gainers:\n", monthly[first_month]["gainers"])
    print("Losers:\n", monthly[first_month]["losers"])
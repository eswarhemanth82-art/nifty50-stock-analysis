"""
app.py
Streamlit dashboard for the Nifty 50 Stock Performance Analysis project.
Run with: streamlit run streamlit_app/app.py
"""

import os
import sys

import pandas as pd
import plotly.express as px
import streamlit as st

# Make scripts/ importable so we can reuse analysis.py functions
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.append(os.path.join(PROJECT_ROOT, "scripts"))

from analysis import (  # noqa: E402
    load_stocks_df,
    load_sector_df,
    get_yearly_returns,
    get_top_green_stocks,
    get_top_loss_stocks,
    get_market_summary,
    get_volatility,
    get_cumulative_returns,
    get_sector_performance,
    get_correlation_matrix,
    get_monthly_gainers_losers,
)

st.set_page_config(page_title="Nifty 50 Stock Dashboard", layout="wide")

st.title("📈 Nifty 50 Stock Performance Dashboard")
st.caption("Data-driven analysis of Nifty 50 stocks over the past year")


@st.cache_data
def load_data():
    df = load_stocks_df()
    yearly_returns_df = get_yearly_returns(df)
    return df, yearly_returns_df


df, yearly_returns_df = load_data()

# ---------------------------------------------------------------------
# Market Summary
# ---------------------------------------------------------------------
st.header("Market Overview")
summary = get_market_summary(df, yearly_returns_df)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Green Stocks", summary["green_stocks"])
col2.metric("Red Stocks", summary["red_stocks"])
col3.metric("Average Price", f"₹{summary['average_price']:,}")
col4.metric("Average Volume", f"{summary['average_volume']:,.0f}")

st.divider()

# ---------------------------------------------------------------------
# Top Green / Loss Stocks
# ---------------------------------------------------------------------
st.header("Top 10 Green vs Loss Stocks")
c1, c2 = st.columns(2)

with c1:
    st.subheader("🟢 Top 10 Green Stocks")
    green = get_top_green_stocks(yearly_returns_df)
    st.dataframe(green.style.format({"yearly_return": "{:.2%}"}), width='stretch')

with c2:
    st.subheader("🔴 Top 10 Loss Stocks")
    red = get_top_loss_stocks(yearly_returns_df)
    st.dataframe(red.style.format({"yearly_return": "{:.2%}"}), width='stretch')

st.divider()

# ---------------------------------------------------------------------
# Volatility
# ---------------------------------------------------------------------
st.header("Volatility Analysis")
vol = get_volatility(df, top_n=10)
fig_vol = px.bar(
    vol, x="symbol", y="volatility",
    title="Top 10 Most Volatile Stocks (Std Dev of Daily Returns)",
    labels={"symbol": "Stock", "volatility": "Volatility"},
)
st.plotly_chart(fig_vol, width='stretch')

st.divider()

# ---------------------------------------------------------------------
# Cumulative Return
# ---------------------------------------------------------------------
st.header("Cumulative Return — Top 5 Performing Stocks")
cum_returns = get_cumulative_returns(df, top_n=5)

cum_df = pd.concat(
    [g.assign(symbol=symbol) for symbol, g in cum_returns.items()],
    ignore_index=True,
)
fig_cum = px.line(
    cum_df, x="date", y="cumulative_return", color="symbol",
    title="Cumulative Return Over Time",
    labels={"date": "Date", "cumulative_return": "Cumulative Return"},
)
st.plotly_chart(fig_cum, width='stretch')

st.divider()

# ---------------------------------------------------------------------
# Sector Performance
# ---------------------------------------------------------------------
st.header("Sector-wise Performance")
try:
    sector_df = load_sector_df()
    sector_perf, _ = get_sector_performance(df, sector_df)
    fig_sector = px.bar(
        sector_perf, x="sector", y="avg_yearly_return",
        title="Average Yearly Return by Sector",
        labels={"sector": "Sector", "avg_yearly_return": "Avg Yearly Return"},
    )
    fig_sector.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig_sector, width='stretch')
except FileNotFoundError as e:
    st.warning(str(e))

st.divider()

# ---------------------------------------------------------------------
# Correlation Heatmap
# ---------------------------------------------------------------------
st.header("Stock Price Correlation")
corr = get_correlation_matrix(df)
fig_corr = px.imshow(
    corr, text_auto=False, aspect="auto",
    title="Correlation Matrix of Closing Prices",
    color_continuous_scale="RdBu_r",
)
st.plotly_chart(fig_corr, width='stretch')

st.divider()

# ---------------------------------------------------------------------
# Monthly Gainers / Losers
# ---------------------------------------------------------------------
st.header("Top 5 Gainers and Losers (Month-wise)")
monthly = get_monthly_gainers_losers(df, top_n=5)
months = sorted(monthly.keys())
selected_month = st.selectbox("Select Month", months, index=len(months) - 1)

m1, m2 = st.columns(2)
with m1:
    st.subheader(f"🟢 Top 5 Gainers — {selected_month}")
    st.dataframe(
        monthly[selected_month]["gainers"].style.format({"monthly_return": "{:.2%}"}),
        width='stretch',
    )
with m2:
    st.subheader(f"🔴 Top 5 Losers — {selected_month}")
    st.dataframe(
        monthly[selected_month]["losers"].style.format({"monthly_return": "{:.2%}"}),
        width='stretch',
    )
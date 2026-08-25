# 📈 Nifty 50 Stock Performance Dashboard

A data-driven analysis and visualization project covering the Nifty 50 stocks' performance over the past year. Raw daily YAML data is extracted, cleaned, loaded into SQL, analyzed, and visualized through both a Streamlit web app and a Power BI dashboard.

## Problem Statement

This project analyzes daily stock data (open, close, high, low, volume) for Nifty 50 stocks, cleans and processes it, and surfaces key performance insights — top/worst performers, volatility, cumulative returns, sector-wise performance, price correlation, and monthly gainers/losers — through interactive dashboards.

## Tech Stack

- **Language:** Python
- **Database:** SQLite (via SQLAlchemy)
- **Visualization:** Streamlit, Power BI
- **Libraries:** Pandas, PyYAML, SQLAlchemy, Plotly, Matplotlib

## Project Structure

```
nifty50-stock-analysis/
├── data/                     # Raw YAML data, organized by month (YYYY-MM/date.yaml)
├── extracted_csv/            # Per-symbol CSVs extracted from YAML (50 files)
├── processed_data/           # Cleaned master_data.csv with daily returns
├── scripts/
│   ├── extract_yaml.py       # Step 1: YAML -> per-symbol CSVs
│   ├── clean_data.py         # Step 2: Combine & clean into master DataFrame
│   ├── load_to_sql.py        # Step 3: Load master data into SQLite
│   └── analysis.py           # Step 4: All 5 required analyses (reusable functions)
├── streamlit_app/
│   └── app.py                # Interactive Streamlit dashboard
├── nifty50_dashboard.pbix    # Power BI dashboard
├── nifty50.db                # SQLite database (stocks table)
├── sector_mapping.csv        # Symbol -> sector mapping
├── requirements.txt
└── README.md
```

## Workflow

1. **Extract** — `extract_yaml.py` walks through `data/<YYYY-MM>/*.yaml`, groups records by stock symbol, and writes one CSV per symbol into `extracted_csv/`.
2. **Clean & Combine** — `clean_data.py` merges all 50 symbol CSVs into a single master DataFrame, sorts by symbol and date, and computes daily returns. Output: `processed_data/master_data.csv`.
3. **Load to SQL** — `load_to_sql.py` loads the cleaned master data into a SQLite database (`nifty50.db`) as a `stocks` table.
4. **Analyze** — `analysis.py` provides reusable functions for all 5 required analyses:
   - Volatility (std dev of daily returns)
   - Cumulative return over time (top 5 performers)
   - Sector-wise average yearly return
   - Stock price correlation matrix
   - Monthly top 5 gainers/losers
5. **Visualize** — Both `streamlit_app/app.py` and `nifty50_dashboard.pbix` consume the same SQLite database / CSVs to present the analysis interactively.

## How to Run

### 1. Clone the repository
```bash
git clone https://github.com/eswarhemanth82-art/nifty50-stock-analysis.git
cd nifty50-stock-analysis
```

### 2. Set up the environment
```bash
python -m venv venv
venv\Scripts\activate      # Windows
pip install -r requirements.txt
```

### 3. Run the pipeline (in order)
```bash
python scripts/extract_yaml.py
python scripts/clean_data.py
python scripts/load_to_sql.py
python scripts/analysis.py     # optional: prints a self-test of all analyses
```

### 4. Launch the Streamlit dashboard
```bash
streamlit run streamlit_app/app.py
```
Opens at `http://localhost:8501`.

### 5. View the Power BI dashboard
Open `nifty50_dashboard.pbix` in Power BI Desktop.

## Key Results

- Ranked top 10 best/worst performing Nifty 50 stocks by yearly return
- Market summary: green vs red stock counts, average price, average volume
- Volatility ranking of the 10 most volatile stocks
- Cumulative return trend for the top 5 performers
- Sector-wise average yearly return comparison
- Full 50x50 stock price correlation heatmap
- Month-wise top 5 gainers and losers
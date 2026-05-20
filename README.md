# Factor Investing Backtest

A Python pipeline for backtesting a momentum-based factor investing strategy using a curated sample of S&P 500 stocks. The project fetches market data, ranks stocks by 12-month momentum, constructs winner and loser portfolios, compares performance to the SPY benchmark, and exports results for analysis.

## Project Structure

- `main.py` — Entry point for the full pipeline.
- `fetch_data.py` — Downloads stock prices from Yahoo Finance and macro data from FRED.
- `factor_screen.py` — Computes annual returns, ranks stocks into momentum quintiles, and selects portfolio groups.
- `backtest.py` — Calculates portfolio returns, benchmark returns, cumulative growth, and performance metrics.
- `export.py` — Saves results to SQLite and exports CSV files for visualization.
- `requirements.txt` — Python dependencies.
- `data/` — Output SQLite database file.
- `outputs/` — Generated CSV results for analysis and Tableau.

## What it does

The strategy follows a simple annual momentum factor:

1. Fetch daily prices for a curated stock universe and the SPY benchmark.
2. Compute year-over-year returns for each stock.
3. Rank stocks into 5 momentum quintiles each year.
4. Build equal-weight portfolios for the top quintile (winners) and bottom quintile (losers).
5. Hold each portfolio for one year and compare performance to SPY.
6. Export annual and cumulative returns for analysis.

## Requirements

- Python 3.8+
- `yfinance`
- `pandas`
- `fredapi`
- `requests`

Install dependencies with:

```bash
python3 -m pip install -r requirements.txt
```

## Usage

Run the full pipeline with:

```bash
python3 main.py
```

This will:

- download stock and benchmark data
- compute factor rankings and portfolio returns
- calculate benchmark and cumulative returns
- save results to `data/backtest.db`
- export CSV files to `outputs/`

## Output Files

Generated CSV files in `outputs/`:

- `annual_returns.csv`
- `cumulative_returns.csv`
- `performance_metrics.csv`
- `annual_returns_long.csv`
- `cumulative_returns_long.csv`

SQLite output:

- `data/backtest.db`

## Notes

- Tickers are currently hard-coded in `fetch_data.py`.
- The strategy is intended for research and should not be used as live trading advice.
- Replace the `FRED_API_KEY` constant in `fetch_data.py` with your own key if required.


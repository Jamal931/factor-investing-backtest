# export.py
# This file saves all backtest results to SQLite
# and exports CSVs for Tableau visualization.

import pandas as pd
import sqlite3
import os

# ── PATHS ─────────────────────────────────────────────────────
DB_PATH      = "data/backtest.db"
OUTPUTS_PATH = "outputs/"


def save_to_sqlite(portfolio_returns, cumulative, metrics, spy_returns):
    """
    Save all backtest results to a SQLite database.
    Creates three tables:
        portfolio_returns  — annual returns per strategy
        cumulative_returns — cumulative growth of $1 invested
        performance_metrics — Sharpe, volatility, drawdown
    """
    print("Saving results to SQLite...")

    # Connect to SQLite — creates the file if it doesn't exist
    conn = sqlite3.connect(DB_PATH)

    # ── TABLE 1: Annual portfolio returns ──────────────────────
    portfolio_returns[["winner_return", "loser_return"]].to_sql(
        "portfolio_returns",
        conn,
        if_exists="replace",  # overwrite if table already exists
        index=True,
        index_label="year"
    )

    # ── TABLE 2: Cumulative returns ────────────────────────────
    cumulative.to_sql(
        "cumulative_returns",
        conn,
        if_exists="replace",
        index=True,
        index_label="year"
    )

    # ── TABLE 3: Performance metrics ──────────────────────────
    metrics.to_sql(
        "performance_metrics",
        conn,
        if_exists="replace",
        index=True,
        index_label="strategy"
    )

    conn.close()
    print(f"Data saved to {DB_PATH}")


def export_to_csv(portfolio_returns, cumulative, metrics):
    """
    Export all results to CSV files for Tableau.
    Tableau connects directly to CSV files — no database 
    connection needed.
    """
    print("Exporting CSVs for Tableau...")

    # ── CSV 1: Annual returns ──────────────────────────────────
    annual_path = os.path.join(OUTPUTS_PATH, "annual_returns.csv")
    portfolio_returns[["winner_return", "loser_return"]].to_csv(
        annual_path
    )
    print(f"  Saved: {annual_path}")

    # ── CSV 2: Cumulative returns ──────────────────────────────
    cumulative_path = os.path.join(OUTPUTS_PATH, "cumulative_returns.csv")
    cumulative.to_csv(cumulative_path)
    print(f"  Saved: {cumulative_path}")

    # ── CSV 3: Performance metrics ─────────────────────────────
    metrics_path = os.path.join(OUTPUTS_PATH, "performance_metrics.csv")
    metrics.to_csv(metrics_path)
    print(f"  Saved: {metrics_path}")

    # ── CSV 4: Annual returns melted for Tableau line chart ────
    # Tableau works better with "long format" data
    # Instead of 3 columns (Winners, Losers, SPY) per row,
    # we create one row per strategy per year
    cumulative_long = cumulative.reset_index().melt(
        id_vars="year",
        var_name="strategy",
        value_name="cumulative_return"
    )
    long_path = os.path.join(OUTPUTS_PATH, "cumulative_returns_long.csv")
    cumulative_long.to_csv(long_path, index=False)
    print(f"  Saved: {long_path}")

    # ── CSV 5: Annual returns melted for Tableau bar chart ─────
    annual_long = portfolio_returns[
        ["winner_return", "loser_return"]
    ].reset_index().melt(
        id_vars="year",
        var_name="strategy",
        value_name="annual_return"
    )
    annual_long_path = os.path.join(
        OUTPUTS_PATH, "annual_returns_long.csv"
    )
    annual_long.to_csv(annual_long_path, index=False)
    print(f"  Saved: {annual_long_path}")


def verify_sqlite():
    """
    Quick check — read back from SQLite and print the tables
    to confirm everything saved correctly.
    """
    print("\nVerifying SQLite database...")
    conn = sqlite3.connect(DB_PATH)

    tables = ["portfolio_returns", "cumulative_returns", 
              "performance_metrics"]

    for table in tables:
        df = pd.read_sql(f"SELECT * FROM {table}", conn)
        print(f"\nTable: {table} ({len(df)} rows)")
        print(df.to_string())

    conn.close()


if __name__ == "__main__":
    from fetch_data import fetch_stock_prices, fetch_sp500_benchmark
    from factor_screen import (compute_annual_returns,
                                rank_stocks_by_momentum,
                                select_portfolios)
    from backtest import (compute_portfolio_returns,
                          compute_benchmark_returns,
                          compute_cumulative_returns,
                          compute_metrics)

    prices          = fetch_stock_prices()
    spy             = fetch_sp500_benchmark()
    annual_returns  = compute_annual_returns(prices)
    quintile_ranks  = rank_stocks_by_momentum(annual_returns)
    winners, losers = select_portfolios(quintile_ranks)

    portfolio_returns = compute_portfolio_returns(
        winners, losers, annual_returns
    )
    spy_returns  = compute_benchmark_returns(spy)
    cumulative   = compute_cumulative_returns(
        portfolio_returns, spy_returns
    )
    metrics      = compute_metrics(portfolio_returns, spy_returns)

    save_to_sqlite(portfolio_returns, cumulative, metrics, spy_returns)
    export_to_csv(portfolio_returns, cumulative, metrics)
    verify_sqlite()

    print("\nAll exports complete. CSVs are in the outputs/ folder.")
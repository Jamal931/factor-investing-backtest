# main.py
# Entry point for the entire factor investing backtest pipeline.
# Run this file to execute all steps in order:
#   1. Fetch data (prices, SPY, FRED)
#   2. Compute factor screen (momentum rankings)
#   3. Run backtest (portfolio returns vs benchmark)
#   4. Export results (SQLite + CSVs for Tableau)

from fetch_data import (fetch_stock_prices, 
                         fetch_sp500_benchmark, 
                         fetch_pe_ratios)

from factor_screen import (compute_annual_returns,
                            rank_stocks_by_momentum,
                            select_portfolios)

from backtest import (compute_portfolio_returns,
                      compute_benchmark_returns,
                      compute_cumulative_returns,
                      compute_metrics)

from export import (save_to_sqlite, 
                    export_to_csv, 
                    verify_sqlite)


def main():
    print("=" * 60)
    print("  FACTOR INVESTING BACKTEST — MOMENTUM STRATEGY")
    print("=" * 60)

    # ── STEP 1: FETCH DATA ─────────────────────────────────────
    print("\n[STEP 1] Fetching market data...")
    prices    = fetch_stock_prices()
    spy       = fetch_sp500_benchmark()
    fred_data = fetch_pe_ratios()

    # ── STEP 2: FACTOR SCREEN ──────────────────────────────────
    print("\n[STEP 2] Running momentum factor screen...")
    annual_returns  = compute_annual_returns(prices)
    quintile_ranks  = rank_stocks_by_momentum(annual_returns)
    winners, losers = select_portfolios(quintile_ranks)

    # ── STEP 3: BACKTEST ───────────────────────────────────────
    print("\n[STEP 3] Running backtest...")
    portfolio_returns = compute_portfolio_returns(
        winners, losers, annual_returns
    )
    spy_returns = compute_benchmark_returns(spy)
    cumulative  = compute_cumulative_returns(
        portfolio_returns, spy_returns
    )
    metrics = compute_metrics(portfolio_returns, spy_returns)

    # ── STEP 4: EXPORT ─────────────────────────────────────────
    print("\n[STEP 4] Exporting results...")
    save_to_sqlite(portfolio_returns, cumulative, metrics, spy_returns)
    export_to_csv(portfolio_returns, cumulative, metrics)

    # ── RESULTS SUMMARY ────────────────────────────────────────
    print("\n" + "=" * 60)
    print("  BACKTEST RESULTS SUMMARY")
    print("=" * 60)
    print("\nPerformance Metrics:")
    print(metrics.to_string())
    print("\nCumulative Returns (final year):")
    print(cumulative.iloc[-1].to_string())
    print("\nCSVs saved to outputs/ — ready for Tableau.")
    print("SQLite database saved to data/backtest.db")
    print("\nDone.")


if __name__ == "__main__":
    main()
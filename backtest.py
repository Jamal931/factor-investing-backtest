# backtest.py
# This file simulates holding the winner and loser portfolios
# each year and calculates their performance vs the SPY benchmark.
# 
# Strategy:
#   - Each year, buy equal-weight positions in the Q5 winner stocks
#   - Hold for exactly one year
#   - Rebalance annually
#   - Compare cumulative returns against SPY buy-and-hold

import pandas as pd
import numpy as np


def compute_portfolio_returns(winners, losers, annual_returns):
    """
    For each year, compute the equal-weighted average return
    of the winner portfolio and the loser portfolio.
    
    winners:        dict of year -> list of winner tickers
    losers:         dict of year -> list of loser tickers
    annual_returns: DataFrame of annual returns per ticker
    
    Returns a DataFrame with columns:
        winners_return, losers_return for each year
    """
    print("Computing portfolio returns...")

    results = []

    for year in annual_returns.index:
        # Skip the first year since we use it to form the portfolio
        # We form the portfolio at end of year T, hold through year T+1
        next_years = annual_returns.index[
            annual_returns.index > year
        ]

        if len(next_years) == 0:
            continue

        next_year = next_years[0]

        # Get the tickers selected at end of current year
        winner_tickers = winners.get(year, [])
        loser_tickers  = losers.get(year, [])

        # Get next year's returns for those tickers
        # Only keep tickers that exist in next year's data
        valid_winners = [t for t in winner_tickers 
                        if t in annual_returns.columns]
        valid_losers  = [t for t in loser_tickers  
                        if t in annual_returns.columns]

        if not valid_winners or not valid_losers:
            continue

        # Equal-weight average return across all winner/loser stocks
        winner_return = annual_returns.loc[next_year, valid_winners].mean()
        loser_return  = annual_returns.loc[next_year, valid_losers].mean()

        results.append({
            "year":           next_year.year,
            "winner_return":  winner_return,
            "loser_return":   loser_return,
            "winner_tickers": valid_winners,
            "loser_tickers":  valid_losers
        })

    portfolio_returns = pd.DataFrame(results).set_index("year")

    print(f"Portfolio returns computed for {len(portfolio_returns)} years")
    return portfolio_returns


def compute_benchmark_returns(spy):
    """
    Compute the annual return of SPY (S&P 500 benchmark)
    for each year in our backtest period.
    
    spy: Series of daily SPY closing prices
    Returns a Series of annual SPY returns indexed by year.
    """
    print("Computing SPY benchmark returns...")

    # Resample to year-end prices
    spy_annual = spy.resample("YE").last()

    # Compute annual percentage change
    spy_returns = spy_annual.pct_change().dropna()

    # Index by year integer for easy merging
    spy_returns.index = spy_returns.index.year

    return spy_returns


def compute_cumulative_returns(portfolio_returns, spy_returns):
    """
    Compute cumulative returns for winners, losers, and SPY.
    Starting value = 1.0 (representing $1 invested at the start).
    
    Cumulative return compounds each year's return:
        cumulative[t] = cumulative[t-1] * (1 + return[t])
    """
    print("Computing cumulative returns...")

    # Align SPY returns to the same years as portfolio returns
    aligned_spy = spy_returns.reindex(portfolio_returns.index).dropna()
    portfolio_returns = portfolio_returns.reindex(aligned_spy.index)

    # Compute cumulative product starting from 1.0
    cum_winners = (1 + portfolio_returns["winner_return"]).cumprod()
    cum_losers  = (1 + portfolio_returns["loser_return"]).cumprod()
    cum_spy     = (1 + aligned_spy).cumprod()

    cumulative = pd.DataFrame({
        "Winners (Q5)": cum_winners,
        "Losers (Q1)":  cum_losers,
        "SPY":          cum_spy
    })

    return cumulative


def compute_metrics(portfolio_returns, spy_returns):
    """
    Compute key performance metrics for the backtest:
        - Annualized return
        - Volatility (standard deviation of annual returns)
        - Sharpe ratio (return per unit of risk, assuming risk-free rate = 0)
        - Max drawdown (largest peak-to-trough decline)
    """
    print("Computing performance metrics...")

    aligned_spy = spy_returns.reindex(portfolio_returns.index).dropna()
    portfolio_returns = portfolio_returns.reindex(aligned_spy.index)

    def sharpe(returns):
        # Sharpe ratio = mean return / std of returns
        # We assume risk-free rate = 0 for simplicity
        return returns.mean() / returns.std() if returns.std() != 0 else 0

    def max_drawdown(returns):
        # Max drawdown = largest peak-to-trough decline
        cumulative = (1 + returns).cumprod()
        rolling_max = cumulative.cummax()
        drawdown = (cumulative - rolling_max) / rolling_max
        return drawdown.min()

    metrics = pd.DataFrame({
        "Annualized Return": [
            portfolio_returns["winner_return"].mean(),
            portfolio_returns["loser_return"].mean(),
            aligned_spy.mean()
        ],
        "Volatility": [
            portfolio_returns["winner_return"].std(),
            portfolio_returns["loser_return"].std(),
            aligned_spy.std()
        ],
        "Sharpe Ratio": [
            sharpe(portfolio_returns["winner_return"]),
            sharpe(portfolio_returns["loser_return"]),
            sharpe(aligned_spy)
        ],
        "Max Drawdown": [
            max_drawdown(portfolio_returns["winner_return"]),
            max_drawdown(portfolio_returns["loser_return"]),
            max_drawdown(aligned_spy)
        ]
    }, index=["Winners (Q5)", "Losers (Q1)", "SPY"])

    return metrics


if __name__ == "__main__":
    from fetch_data import fetch_stock_prices, fetch_sp500_benchmark
    from factor_screen import (compute_annual_returns, 
                                rank_stocks_by_momentum, 
                                select_portfolios)

    prices          = fetch_stock_prices()
    spy             = fetch_sp500_benchmark()
    annual_returns  = compute_annual_returns(prices)
    quintile_ranks  = rank_stocks_by_momentum(annual_returns)
    winners, losers = select_portfolios(quintile_ranks)

    portfolio_returns = compute_portfolio_returns(
        winners, losers, annual_returns
    )
    spy_returns    = compute_benchmark_returns(spy)
    cumulative     = compute_cumulative_returns(
        portfolio_returns, spy_returns
    )
    metrics        = compute_metrics(portfolio_returns, spy_returns)

    print("\nAnnual Portfolio Returns:")
    print(portfolio_returns[["winner_return", "loser_return"]])
    print("\nCumulative Returns:")
    print(cumulative)
    print("\nPerformance Metrics:")
    print(metrics.to_string())
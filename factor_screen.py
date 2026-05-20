# factor_screen.py
# This file computes the momentum factor for each stock
# and ranks them into quintiles for portfolio construction.
# Momentum factor = a stock's return over the past 12 months.
# Stocks with the highest 12-month return are expected to 
# continue outperforming — this is one of the most well-documented
# factors in finance (Jegadeesh & Titman, 1993).

import pandas as pd
import numpy as np

def compute_annual_returns(prices):
    """
    Compute each stock's return over the past 12 months
    for every year in our date range.
    
    prices: DataFrame where columns are tickers and rows are dates.
    Returns a DataFrame of annual returns indexed by year.
    """
    print("Computing annual returns...")

    # Resample daily prices to get the last price of each year
    # 'YE' means year-end frequency
    annual_prices = prices.resample("YE").last()

    # Compute the percentage change from one year-end to the next
    # This gives us each stock's return over that year
    annual_returns = annual_prices.pct_change().dropna()

    print(f"Annual returns computed for {annual_returns.shape[1]} tickers "
          f"across {annual_returns.shape[0]} years")

    return annual_returns


def rank_stocks_by_momentum(annual_returns):
    """
    Rank stocks each year by their 12-month return (momentum factor).
    Divide them into 5 quintiles:
        Q1 = bottom 20% (lowest momentum — losers)
        Q5 = top 20%    (highest momentum — winners)
    
    Returns a DataFrame of quintile labels (1-5) for each stock each year.
    """
    print("Ranking stocks by momentum factor...")

    # For each row (year), rank every stock's return into quintiles
    # qcut divides into 5 equal-sized buckets
    # labels=False gives us 0-4, we add 1 to get 1-5
    quintile_ranks = annual_returns.apply(
        lambda row: pd.qcut(row.rank(method="first"), 
                           q=5, 
                           labels=[1, 2, 3, 4, 5]).astype(int),
        axis=1
    )

    return quintile_ranks


def select_portfolios(quintile_ranks):
    """
    Select the top quintile (Q5 — momentum winners) 
    and bottom quintile (Q1 — momentum losers) each year.
    
    Returns two DataFrames:
        winners: stocks in Q5 each year
        losers:  stocks in Q1 each year
    """
    print("Selecting winner and loser portfolios...")

    winners = {}  # year -> list of winner tickers
    losers  = {}  # year -> list of loser tickers

    for year in quintile_ranks.index:
        row = quintile_ranks.loc[year]
        
        # Q5 = top momentum stocks (winners)
        winners[year] = row[row == 5].index.tolist()
        
        # Q1 = bottom momentum stocks (losers)
        losers[year]  = row[row == 1].index.tolist()

    print(f"Portfolios selected for {len(winners)} years")

    # Show a sample of winners and losers for the first year
    first_year = list(winners.keys())[0]
    print(f"\nSample — {first_year.year} Winners: {winners[first_year]}")
    print(f"Sample — {first_year.year} Losers:  {losers[first_year]}")

    return winners, losers


if __name__ == "__main__":
    # Test this file directly using data from fetch_data.py
    from fetch_data import fetch_stock_prices

    prices         = fetch_stock_prices()
    annual_returns = compute_annual_returns(prices)
    quintile_ranks = rank_stocks_by_momentum(annual_returns)
    winners, losers = select_portfolios(quintile_ranks)

    print("\nAnnual returns sample:")
    print(annual_returns.head(3))
    print("\nQuintile ranks sample:")
    print(quintile_ranks.head(3))
# fetch_data.py
# This file handles all data pulling — stock prices from yFinance 
# and macro data from FRED API

import yfinance as yf
import pandas as pd
from fredapi import Fred
import os

# ── FRED API KEY ──────────────────────────────────────────────
FRED_API_KEY = "f90b841675f42ba3822737e78c24ff10"

# ── S&P 500 TICKERS ───────────────────────────────────────────

TICKERS = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "META",   # Technology
    "JPM", "BAC", "GS", "WFC", "MS",            # Financials
    "JNJ", "PFE", "UNH", "MRK", "ABT",          # Healthcare
    "XOM", "CVX", "COP", "SLB", "EOG",          # Energy
    "HD", "MCD", "NKE", "SBUX", "TGT",          # Consumer
    "CAT", "BA", "GE", "MMM", "HON"             # Industrials
]

# ── DATE RANGE ────────────────────────────────────────────────
# We are backtesting over 10 years of data
START_DATE = "2014-01-01"
END_DATE   = "2024-01-01"


def fetch_stock_prices():
    """
    Pull daily closing prices for all tickers from yFinance.
    Returns a DataFrame where each column is a ticker 
    and each row is a date.
    """
    print("Fetching stock prices from yFinance...")

    # yf.download pulls historical price data for all tickers at once
    # auto_adjust=True adjusts for splits and dividends automatically
    prices = yf.download(
        TICKERS,
        start=START_DATE,
        end=END_DATE,
        auto_adjust=True,
        progress=False
    )

    # We only want the closing price column, not Open/High/Low/Volume
    prices = prices["Close"]

    # Drop any tickers that have too much missing data
    # thresh=len(prices)*0.8 means keep columns with at least 80% of data
    prices = prices.dropna(thresh=int(len(prices) * 0.8), axis=1)

    print(f"Fetched prices for {prices.shape[1]} tickers")
    return prices


def fetch_sp500_benchmark():
    """
    Pull the S&P 500 index (SPY ETF) as our benchmark.
    We will compare our factor portfolio returns against this.
    """
    print("Fetching S&P 500 benchmark (SPY)...")

    spy = yf.download(
        "SPY",
        start=START_DATE,
        end=END_DATE,
        auto_adjust=True,
        progress=False
    )

    # Newer yFinance returns a MultiIndex DataFrame
    # We flatten it and grab just the Close column
    if isinstance(spy.columns, pd.MultiIndex):
        spy = spy["Close"]
        if isinstance(spy, pd.DataFrame):
            spy = spy.iloc[:, 0]
    else:
        spy = spy["Close"]

    # Rename the Series to SPY
    spy.name = "SPY"

    return spy


def fetch_pe_ratios():
    """
    Pull P/E ratio proxy data from FRED.
    We use the Shiller CAPE ratio (MULTPL) as a macro P/E signal,
    and compute individual stock P/E from earnings data.
    
    For simplicity we use a manually curated P/E snapshot — 
    in a production system you would pull this from a 
    paid financial data API like Financial Modeling Prep.
    """
    print("Fetching macro data from FRED...")

    fred = Fred(api_key=FRED_API_KEY)

    # Pull the S&P 500 Earnings Per Share from FRED
    # Series ID: SP500EPS — quarterly S&P 500 earnings
    try:
        sp500_eps = fred.get_series("SPASTT01USM661N", START_DATE, END_DATE)
        sp500_eps = pd.DataFrame(sp500_eps, columns=["SP500_EPS"])
        sp500_eps.index.name = "date"
        print("FRED data fetched successfully")
    except Exception as e:
        print(f"FRED error: {e}")
        sp500_eps = pd.DataFrame()

    return sp500_eps


if __name__ == "__main__":
    # Test all three functions when you run this file directly
    prices   = fetch_stock_prices()
    spy      = fetch_sp500_benchmark()
    sp500_eps = fetch_pe_ratios()

    print("\nPrices shape:", prices.shape)
    print("SPY shape:", spy.shape)
    print("FRED data shape:", sp500_eps.shape)
    print("\nFirst 3 rows of prices:")
    print(prices.head(3))

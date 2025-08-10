"""
strategy.py
Implements trading strategy (RSI + SMA crossover) and saves signals for backtesting.
"""

import pandas as pd
import logging
from data_fetcher import fetch_all_data
from indicators import add_indicators_to_all
from config import TICKERS

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def apply_strategy(df):
    """
    Apply RSI < 30 and SMA20 > SMA50 for BUY.
    RSI > 70 and SMA20 < SMA50 for SELL.
    Else HOLD.
    """
    df["Signal"] = "HOLD"

    # BUY condition
    buy_cond = (df["RSI"] < 30) & (df["SMA20"] > df["SMA50"])
    df.loc[buy_cond, "Signal"] = "BUY"

    # SELL condition
    sell_cond = (df["RSI"] > 70) & (df["SMA20"] < df["SMA50"])
    df.loc[sell_cond, "Signal"] = "SELL"

    return df

def apply_strategy_to_all(data_dict):
    """Apply strategy to all tickers and return updated dict."""
    updated_data = {}
    for ticker, df in data_dict.items():
        logging.info(f"📊 Processing strategy for {ticker} ...")
        df_with_signals = apply_strategy(df)
        updated_data[ticker] = df_with_signals
        logging.info(f"✅ Signals generated for {ticker} ({df_with_signals['Signal'].value_counts().to_dict()})")
    return updated_data

if __name__ == "__main__":
    # 1. Fetch raw data (dummy or real)
    logging.info("📂 Loading local dataset from nifty_data.xlsx ...")
    raw_data = pd.read_excel("nifty_data.xlsx", sheet_name=None)  # dict of DataFrames

    # 2. Add indicators
    data_with_indicators = add_indicators_to_all(raw_data)

    # 3. Apply strategy
    data_with_signals = apply_strategy_to_all(data_with_indicators)

    # 4. Save output for backtesting
    output_file = "nifty_data_with_signals.xlsx"
    with pd.ExcelWriter(output_file) as writer:
        for ticker, df in data_with_signals.items():
            df.to_excel(writer, sheet_name=ticker, index=True)
    logging.info(f"💾 Strategy output saved to {output_file}")

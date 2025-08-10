"""
utils.py
Utility functions for NiftyBot.
"""

import logging
import pandas as pd


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )


def df_to_list_of_lists(df):
    """
    Converts a DataFrame into list-of-lists format for Google Sheets upload.
    """
    return [df.columns.tolist()] + df.values.tolist()


def filter_trade_signals(df):
    """
    Returns only the rows where a trade signal occurred (Signal != 0).
    """
    return df[df["Signal"] != 0]


def merge_trade_logs(data_dict):
    """
    Combines trade logs from multiple tickers into a single DataFrame.
    """
    logs = []
    for ticker, df in data_dict.items():
        trades = filter_trade_signals(df)
        trades.insert(0, "Ticker", ticker)
        logs.append(trades)
    return pd.concat(logs) if logs else pd.DataFrame()

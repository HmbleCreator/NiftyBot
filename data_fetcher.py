"""
data_fetcher.py - Fetch NSE stock data using yfinance or load from local Excel
"""

import pandas as pd
import logging
import yfinance as yf
from config import TICKERS, DATA_PERIOD, DATA_INTERVAL
from datetime import datetime, timedelta
import os

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def period_to_dates(period):
    """
    Convert period string like '6mo', '1y' into (start_date, end_date) datetime objects.
    Defaults to 6 months if unknown.
    """
    end = datetime.today()
    start = end - timedelta(days=180)  # default 6 months

    if isinstance(period, str):
        p = period.lower().strip()
        try:
            if p.endswith("mo"):
                months = int(p.replace("mo", ""))
                start = end - timedelta(days=months * 30)
            elif p.endswith("y"):
                years = int(p.replace("y", ""))
                start = end - timedelta(days=years * 365)
        except Exception:
            pass

    return start, end


def fetch_data_yf(ticker, start_date, end_date, interval=DATA_INTERVAL):
    """
    Fetch historical OHLCV data for a single NSE ticker using yfinance.
    """
    try:
        logging.info(f"📈 Fetching {ticker} from Yahoo Finance {start_date.date()} → {end_date.date()}...")
        df = yf.download(ticker, start=start_date, end=end_date, interval=interval)
        df.dropna(inplace=True)

        if df.empty:
            logging.warning(f"No data returned for {ticker}")
        else:
            logging.info(f"✅ Data fetched for {ticker} ({len(df)} rows)")

        return df

    except Exception as e:
        logging.error(f"❌ Failed to fetch {ticker}: {e}")
        return pd.DataFrame()


def fetch_all_data(tickers=None, period=DATA_PERIOD, interval=DATA_INTERVAL, use_local=False, local_file="nifty_data.xlsx"):
    """
    Fetch data for all tickers using yfinance or load from local Excel.
    If use_local=True, load pre-saved data from Excel file.
    """
    if tickers is None:
        tickers = TICKERS

    if use_local:
        if not os.path.exists(local_file):
            logging.error(f"❌ Local file {local_file} not found.")
            return {}

        logging.info(f"📂 Loading local dataset from {local_file} ...")
        xls = pd.ExcelFile(local_file)
        all_data = {}
        for sheet in xls.sheet_names:
            df = pd.read_excel(xls, sheet_name=sheet)
            # Ensure Date is index
            if "Date" in df.columns:
                df["Date"] = pd.to_datetime(df["Date"])
                df.set_index("Date", inplace=True)
            else:
                df.index = pd.to_datetime(df.index)

            all_data[sheet] = df
            logging.info(f"✅ Loaded {sheet} ({len(df)} rows) from local file.")
        return all_data

    else:
        start_date, end_date = period_to_dates(period)
        all_data = {}
        for ticker in tickers:
            df = fetch_data_yf(ticker, start_date, end_date, interval)
            if not df.empty:
                all_data[ticker] = df
        return all_data


if __name__ == "__main__":
    # Example: Load from local file
    data = fetch_all_data(use_local=True)
    for tkr, df in data.items():
        print(f"\n{tkr} head:")
        print(df.head())

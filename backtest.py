"""
backtest.py
Backtesting utilities for NiftyBot.

Provides:
- backtest(df, initial_capital=100000) -> (trades_df, summary_dict)
- backtest_all(data_dict, initial_capital=100000, months=6) -> (results_dict, summaries_dict)

Execution rules:
- Buy/Sell executions happen at the NEXT trading day's Open (if available), otherwise NEXT Close.
- If a position remains open at the end of the backtest window, it will be closed at the last available Close.
"""

import pandas as pd
import logging
from datetime import datetime
import numpy as np

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def _ensure_datetime_index(df):
    """Ensure the DataFrame has a DateTimeIndex and is sorted ascending."""
    df = df.copy()
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"])
        df.set_index("Date", inplace=True)
    else:
        # If index isn't datetime, try to convert
        if not isinstance(df.index, pd.DatetimeIndex):
            try:
                df.index = pd.to_datetime(df.index)
            except Exception:
                pass
    df = df.sort_index()
    return df


def _normalize_signal(val):
    """Normalize signal values to 'BUY'/'SELL'/'HOLD'."""
    if pd.isna(val):
        return "HOLD"
    if isinstance(val, (int, float, np.integer, np.floating)):
        try:
            v = int(val)
            if v == 1:
                return "BUY"
            if v == -1:
                return "SELL"
            return "HOLD"
        except Exception:
            return "HOLD"
    s = str(val).strip().upper()
    if s in ("BUY", "B", "1"):
        return "BUY"
    if s in ("SELL", "S", "-1"):
        return "SELL"
    return "HOLD"


def backtest(df, initial_capital=100000):
    """
    Run a backtest on a single DataFrame df that contains at least:
      ['Open','Close','Signal'] and a DateTimeIndex.

    Returns:
      trades_df (DataFrame) with columns:
        ['Entry Date','Entry Price','Exit Date','Exit Price','Qty','P&L']
      summary (dict) with keys:
        Final Capital, Total Trades, Wins, Win Ratio (%), Total P&L, Return (%)
    """
    df = _ensure_datetime_index(df)

    # require at least 2 rows & 'Signal' column
    if len(df) < 2 or "Signal" not in df.columns:
        return pd.DataFrame(), {
            "Final Capital": initial_capital,
            "Total Trades": 0,
            "Wins": 0,
            "Win Ratio (%)": 0.0,
            "Total P&L": 0.0,
            "Return (%)": 0.0
        }

    # ensure numeric prices
    if "Open" not in df.columns:
        logging.warning("No 'Open' column present, will use 'Close' for execution.")
    for col in ("Open", "Close"):
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    trades = []
    in_position = False
    entry_price = None
    entry_qty = None
    capital = float(initial_capital)
    idx = df.index.to_list()

    # iterate over rows but execute at next row's price
    for i in range(len(df) - 1):
        sig = _normalize_signal(df["Signal"].iloc[i])
        next_row = df.iloc[i + 1]
        exec_price = None
        if "Open" in df.columns and not pd.isna(next_row.get("Open")):
            exec_price = float(next_row["Open"])
        elif "Close" in df.columns and not pd.isna(next_row.get("Close")):
            exec_price = float(next_row["Close"])
        else:
            continue  # cannot execute without price

        exec_date = idx[i + 1]

        if sig == "BUY" and not in_position:
            entry_price = exec_price
            entry_qty = capital / entry_price if entry_price > 0 else 0
            in_position = True
            trades.append({
                "Entry Date": exec_date,
                "Entry Price": entry_price,
                "Exit Date": pd.NaT,
                "Exit Price": np.nan,
                "Qty": entry_qty,
                "P&L": np.nan
            })

        elif sig == "SELL" and in_position:
            exit_price = exec_price
            exit_date = exec_date
            pnl = (exit_price - entry_price) * entry_qty
            capital = entry_qty * exit_price
            trades[-1].update({
                "Exit Date": exit_date,
                "Exit Price": exit_price,
                "P&L": pnl
            })
            in_position = False
            entry_price = None
            entry_qty = None

    # If still in position at the end, close at last available price
    if in_position:
        last_price = None
        last_date = idx[-1]
        last_row = df.iloc[-1]
        if "Close" in df.columns and not pd.isna(last_row.get("Close")):
            last_price = float(last_row["Close"])
        elif "Open" in df.columns and not pd.isna(last_row.get("Open")):
            last_price = float(last_row["Open"])

        if last_price is not None:
            pnl = (last_price - entry_price) * entry_qty
            capital = entry_qty * last_price
            trades[-1].update({
                "Exit Date": last_date,
                "Exit Price": last_price,
                "P&L": pnl
            })
        in_position = False

    # Build trades DataFrame
    trades_df = pd.DataFrame(trades)

    # Handle case: no trades at all
    if trades_df.empty:
        return trades_df, {
            "Final Capital": float(capital),
            "Total Trades": 0,
            "Wins": 0,
            "Win Ratio (%)": 0.0,
            "Total P&L": 0.0,
            "Return (%)": round(((capital - initial_capital) / initial_capital) * 100, 2)
        }

    # Filter completed trades only
    if "Exit Date" not in trades_df.columns:
        trades_df["Exit Date"] = pd.NaT
    completed = trades_df.dropna(subset=["Exit Date"]).copy()

    # If no completed trades, return zero summary
    if completed.empty:
        return completed.reset_index(drop=True), {
            "Final Capital": float(capital),
            "Total Trades": 0,
            "Wins": 0,
            "Win Ratio (%)": 0.0,
            "Total P&L": 0.0,
            "Return (%)": round(((capital - initial_capital) / initial_capital) * 100, 2)
        }

    # Ensure P&L numeric
    completed["P&L"] = pd.to_numeric(completed["P&L"], errors="coerce").fillna(0.0)

    # Summaries
    total_trades = len(completed)
    wins = (completed["P&L"] > 0).sum()
    total_pnl = completed["P&L"].sum()
    win_ratio = round((wins / total_trades * 100), 2) if total_trades > 0 else 0.0
    total_return_pct = round(((capital - initial_capital) / initial_capital) * 100, 2)

    summary = {
        "Final Capital": float(capital),
        "Total Trades": int(total_trades),
        "Wins": int(wins),
        "Win Ratio (%)": float(win_ratio),
        "Total P&L": float(total_pnl),
        "Return (%)": float(total_return_pct)
    }

    return completed.reset_index(drop=True), summary


def backtest_all(data_dict, initial_capital=100000, months=6):
    """
    Run backtest for multiple tickers.
    Inputs:
      data_dict: { ticker: DataFrame(with signals) }
      initial_capital: money allocated per ticker (default 100,000)
      months: how many months to backtest (slices last 'months' months of each df)
    Returns:
      results: dict mapping ticker -> trades_df
      summaries: dict mapping ticker -> summary dict
    """
    results = {}
    summaries = {}

    for ticker, df in data_dict.items():
        try:
            logging.info(f"🔄 Backtesting {ticker} (last {months} months)...")
            df_local = _ensure_datetime_index(df)

            # slice to last `months` using the last available date in df
            if len(df_local) == 0:
                logging.warning(f"No data for {ticker}. Skipping.")
                continue
            last_date = df_local.index.max()
            start_date = last_date - pd.DateOffset(months=months)
            df_slice = df_local.loc[start_date:last_date].copy()

            if df_slice.empty or "Signal" not in df_slice.columns:
                logging.warning(f"⚠ No valid slice or 'Signal' column for {ticker}. Skipping...")
                results[ticker] = pd.DataFrame()
                summaries[ticker] = {
                    "Final Capital": float(initial_capital),
                    "Total Trades": 0,
                    "Wins": 0,
                    "Win Ratio (%)": 0.0,
                    "Total P&L": 0.0,
                    "Return (%)": 0.0
                }
                continue

            trades_df, summary = backtest(df_slice, initial_capital=initial_capital)
            results[ticker] = trades_df
            summaries[ticker] = summary

            logging.info(f"📊 {ticker} - Final Value: ₹{summary['Final Capital']:.2f} | Return: {summary['Return (%)']:.2f}% | Trades: {summary['Total Trades']}")

        except Exception as e:
            logging.error(f"❌ Error backtesting {ticker}: {e}")
            results[ticker] = pd.DataFrame()
            summaries[ticker] = {
                "Final Capital": float(initial_capital),
                "Total Trades": 0,
                "Wins": 0,
                "Win Ratio (%)": 0.0,
                "Total P&L": 0.0,
                "Return (%)": 0.0
            }

    return results, summaries


if __name__ == "__main__":
    # Quick CLI test: load the signals file if present
    try:
        logging.info("📂 Loading strategy output from nifty_data_with_signals.xlsx ...")
        data_dict = pd.read_excel("nifty_data_with_signals.xlsx", sheet_name=None)
        # ensure 'Date' column becomes index for each sheet
        for t, df in data_dict.items():
            if "Date" in df.columns:
                df["Date"] = pd.to_datetime(df["Date"])
                df.set_index("Date", inplace=True)
            data_dict[t] = df

        results, summaries = backtest_all(data_dict)
        for t in summaries:
            logging.info(f"{t} summary: {summaries[t]}")
    except FileNotFoundError:
        logging.error("nifty_data_with_signals.xlsx not found. Run strategy.py first to create it.")

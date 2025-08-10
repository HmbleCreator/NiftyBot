"""
main.py
Main orchestrator for NiftyBot Algo-Trading System with CLI options.
"""

import logging
import argparse
from data_fetcher import fetch_all_data
from indicators import add_indicators_to_all
from strategy import apply_strategy_to_all
from backtest import backtest_all
from google_sheets import log_trade_data, log_pnl_data, log_summary_data
from ml_model import train_model
from alerts import send_trade_alerts
from utils import setup_logging


def run_niftybot(use_ml=False, use_telegram=False, backtest_mode=False,
                 symbols=None, time_frame=None, period=None, use_dummy=False):
    setup_logging()
    logging.info("🚀 Starting NiftyBot pipeline...")

    # Step 1: Fetch data (API or Dummy Excel)
    raw_data = fetch_all_data(
        tickers=symbols or None,
        period=period,
        interval=time_frame,
        use_local=use_dummy
    )

    # Step 2: Add indicators
    data_with_indicators = add_indicators_to_all(raw_data)

    # Step 3: Apply strategy logic
    data_with_signals = apply_strategy_to_all(data_with_indicators)

    # Step 4: Backtest (if requested)
    summaries = {}
    backtest_results = {}
    if backtest_mode:
        logging.info("📈 Running backtest...")
        backtest_results, summaries = backtest_all(data_with_signals)

        # Ensure ML Accuracy field exists for all tickers (default '-')
        for ticker in summaries:
            summaries[ticker]["ML Accuracy"] = "-"

        # Step 5: ML predictions (if enabled)
        if use_ml:
            logging.info("🤖 Training ML models...")
            for ticker, df in data_with_indicators.items():
                model, acc, pred_signal = train_model(df)
                summaries.setdefault(ticker, {})["ML Accuracy"] = round(acc * 100, 2)
                summaries[ticker]["ML Prediction"] = pred_signal
                logging.info(f"{ticker} - ML Accuracy: {acc:.2%} | Next-Day: {pred_signal}")


    # Step 7: Send Telegram alerts (if enabled)
    if use_telegram:
        logging.info("📢 Sending Telegram alerts...")
        send_trade_alerts(data_with_signals, lookback_days=1)


    logging.info("✅ NiftyBot run complete!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="NiftyBot Algo-Trading System")

    parser.add_argument("--use-ml", action="store_true",
                        help="Run ML predictions")
    parser.add_argument("--use-telegram", action="store_true",
                        help="Send Telegram alerts")
    parser.add_argument("--backtest", action="store_true",
                        help="Run backtest and log results to Google Sheets")
    parser.add_argument("--symbols", nargs="+",
                        help="List of stock symbols (e.g., RELIANCE.NS TCS.NS)")
    parser.add_argument("--time-frame", type=str,
                        help="Data interval (e.g., 1d, 15m)")
    parser.add_argument("--period", type=str,
                        help="Data period (e.g., 6mo, 1y)")
    parser.add_argument("--use-dummy", action="store_true",
                        help="Load data from local Excel file instead of fetching from API")

    args = parser.parse_args()

    run_niftybot(
        use_ml=args.use_ml,
        use_telegram=args.use_telegram,
        backtest_mode=args.backtest,
        symbols=args.symbols,
        time_frame=args.time_frame,
        period=args.period,
        use_dummy=args.use_dummy
    )

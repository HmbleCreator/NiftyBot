import requests
from datetime import datetime, timedelta
import pandas as pd

# 🔹 Set your bot token and chat ID
TELEGRAM_TOKEN = "Put Your Telegram Bot Token Here"
TELEGRAM_CHAT_ID = "Put Your Telegram Chat ID Here"

def send_telegram_message(message):
    """Send a message to the configured Telegram chat."""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    try:
        print(f"Sending Telegram message: {message}")  # Debug print
        response = requests.post(url, data=payload, timeout=5)
        if response.status_code != 200:
            print(f"⚠️ Telegram API error: {response.text}")
    except Exception as e:
        print(f"Telegram send error: {e}")

def send_trade_alerts(data_dict, lookback_days=1):
    """
    Sends Telegram alerts for all BUY/SELL signals within the last `lookback_days`.
    
    Parameters:
    - data_dict: dict[str, pd.DataFrame] {ticker: dataframe_with_signals}
    - lookback_days: int, number of past days to check for alerts
    """
    cutoff_date = datetime.now() - timedelta(days=lookback_days)

    # 📢 Send a startup test alert
    send_telegram_message("✅ Bot started successfully — monitoring for trade signals...")

    for ticker, df in data_dict.items():
        # Ensure index is datetime
        if not isinstance(df.index, pd.DatetimeIndex):
            df.index = pd.to_datetime(df.index, errors="coerce")

        # Filter for recent signals (BUY=1, SELL=-1)
        recent_signals = df[(df["Signal"] != 0) & (df.index >= cutoff_date)]

        for date, row in recent_signals.iterrows():
            signal_type = "BUY" if row["Signal"] == 1 else "SELL"
            emoji = "📈" if signal_type == "BUY" else "📉"
            price = f"{row['Close']:.2f}"
            message = f"{emoji} {signal_type} for {ticker} at ₹{price} on {date.strftime('%Y-%m-%d')}"
            
            print(f"Preparing to send alert: {message}")
            send_telegram_message(message)

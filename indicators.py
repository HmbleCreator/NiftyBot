
## Calculate technical indicators for all stock DataFrames.


import pandas as pd
import logging
import ta  # pip install ta

# Indicator settings
RSI_WINDOW = 14
SMA_FAST = 20
SMA_SLOW = 50
MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9


def add_indicators(df):
    """
    Add RSI, moving averages, and MACD to the DataFrame.
    Assumes DataFrame has columns: Date, Open, High, Low, Close, Volume
    """

    # Ensure datetime index for consistency
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'])
        df.set_index('Date', inplace=True)

    # RSI
    df['RSI'] = ta.momentum.RSIIndicator(
        close=df['Close'],
        window=RSI_WINDOW
    ).rsi()

    # Moving averages
    df['SMA20'] = df['Close'].rolling(window=SMA_FAST).mean()
    df['SMA50'] = df['Close'].rolling(window=SMA_SLOW).mean()

    # MACD
    macd_indicator = ta.trend.MACD(
        close=df['Close'],
        window_slow=MACD_SLOW,
        window_fast=MACD_FAST,
        window_sign=MACD_SIGNAL
    )
    df['MACD'] = macd_indicator.macd()
    df['MACD_SIGNAL'] = macd_indicator.macd_signal()
    df['MACD_HIST'] = macd_indicator.macd_diff()

    df.dropna(inplace=True)  # remove rows with NaN from indicators
    return df


def add_indicators_to_all(data_dict):
    """
    Apply add_indicators() to a dictionary of {ticker: DataFrame}
    """
    result = {}
    for ticker, df in data_dict.items():
        try:
            logging.info(f"📊 Adding indicators for {ticker}...")
            result[ticker] = add_indicators(df.copy())
            logging.info(f"✅ Indicators added for {ticker} ({len(result[ticker])} rows)")
        except Exception as e:
            logging.error(f"❌ Failed to add indicators for {ticker}: {e}")
    return result


if __name__ == "__main__":
    # Quick test with dummy file
    dummy = pd.read_excel("nifty_data.xlsx", sheet_name="RELIANCE.NS")
    dummy_with_ind = add_indicators(dummy)
    print(dummy_with_ind.head())

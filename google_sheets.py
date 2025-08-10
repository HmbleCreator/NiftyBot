
## Automates logging of trades, P&L, and summary statistics to Google Sheets.


import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from config import (
    GOOGLE_CREDENTIALS_FILE,
    GOOGLE_SHEET_NAME,
    TRADE_LOG_SHEET,
    PNL_SHEET,
    SUMMARY_SHEET
)


def get_gsheets_client():
    """Authenticate and return gspread client."""
    scope = ["https://spreadsheets.google.com/feeds",
             "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(GOOGLE_CREDENTIALS_FILE, scope)
    client = gspread.authorize(creds)
    return client


def write_dataframe_to_sheet(df, sheet_name):
    """
    Writes a pandas DataFrame to a specific Google Sheets tab.
    Overwrites existing content.
    """
    client = get_gsheets_client()
    sheet = client.open(GOOGLE_SHEET_NAME).worksheet(sheet_name)

    # Clear the sheet before writing
    sheet.clear()

    # Convert DataFrame to list of lists
    data = [df.columns.tolist()] + df.values.tolist()
    sheet.update("A1", data)


def log_trade_data(trade_data_dict):
    """
    trade_data_dict format: {ticker: DataFrame_with_trades}
    Writes all trades to TRADE_LOG_SHEET.
    """
    combined_trades = []
    for ticker, df in trade_data_dict.items():
        trades = df[df["Signal"] != 0].copy()
        trades.insert(0, "Ticker", ticker)
        combined_trades.append(trades)
    
    if combined_trades:
        trades_df = pd.concat(combined_trades)
        write_dataframe_to_sheet(trades_df, TRADE_LOG_SHEET)


def log_pnl_data(summary_dict):
    """
    Logs final portfolio value and return % from backtest summaries.
    summary_dict: {ticker: {"Final Capital": ..., "Return (%)": ...}}
    """
    pnl_rows = []
    for ticker, stats in summary_dict.items():
        pnl_rows.append([
            ticker,
            stats.get("Final Capital", 0.0),
            stats.get("Return (%)", 0.0)
        ])

    pnl_df = pd.DataFrame(pnl_rows, columns=["Ticker", "Final Portfolio Value", "Return (%)"])
    write_dataframe_to_sheet(pnl_df, PNL_SHEET)




def log_summary_data(summary_dict):
    """
    summary_dict format: {ticker: summary_stats_dict}
    Writes summary statistics to SUMMARY_SHEET.
    """
    summary_df = pd.DataFrame.from_dict(summary_dict, orient="index").reset_index()
    summary_df.rename(columns={"index": "Ticker"}, inplace=True)
    write_dataframe_to_sheet(summary_df, SUMMARY_SHEET)


if __name__ == "__main__":
    # Example test with fake data
    test_df = pd.DataFrame({
        "Close": [100, 102, 101],
        "Signal": [0, 1, -1],
        "Portfolio_Value": [100000, 101000, 100500]
    })
    log_trade_data({"RELIANCE.NS": test_df})
    log_pnl_data({"RELIANCE.NS": test_df})
    log_summary_data({"RELIANCE.NS": {"Total Return (%)": 1.5, "Win Ratio": 0.5}})
    print("✅ Test logging complete")


##################### Google Sheets API Settings ####################
GOOGLE_CREDENTIALS_FILE = "capable-asset-468407-h9-dbda93abc544.json"

# Google Sheets document name
GOOGLE_SHEET_NAME ="NiftyBot_Trade_log"

# Worksheet tab names
TRADE_LOG_SHEET = "Trade Log"
PNL_SHEET = "P&L"
SUMMARY_SHEET ="Summary"


####################### TELEGRAM BOT SETTINGS ########################

# Telegram bot token from BotFather
TELEGRAM_BOT_TOKEN = "Put your Telegram Bot Token here"

# Your Telegram chat ID
TELEGRAM_CHAT_ID = "Put your Telegram Chat ID here"


######################## STRATEGY SETTINGS ############################
RSI_WINDOW = 14                     # industry standard for RSI calculation
SHORT_MA_WINDOW = 20                # 20-day moving average (20-DMA)
LONG_MA_WINDOW = 50                 # 50-day moving average (50-DMA)

RSI_BUY_THRESHOLD = 30              # below = oversold
RSI_SELL_THRESHOLD = 70             # above = overbought


######################## BACKTESTING SETTINGS #############################
INITIAL_CAPITAL = 100000            # Starting Capital for Backtesting

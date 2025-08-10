# NiftyBot - Algorithmic Trading System

NiftyBot is a sophisticated algorithmic trading system designed for the Indian stock market, specifically targeting NIFTY 50 stocks. It combines technical analysis, machine learning predictions, and automated trading signals to provide comprehensive market insights and trading opportunities.

## 🚀 Features

- **Multi-Asset Support**: Tracks and analyzes NIFTY 50 stocks
- **Technical Indicators**: RSI, SMA20, SMA50 for comprehensive market analysis
- **Machine Learning**: Optional ML-based trading signals with accuracy metrics
- **Backtesting Engine**: Test strategies against historical data
- **Google Sheets Integration**: Automatic logging of trades, P&L, and summaries
- **Telegram Alerts**: Real-time notifications for trading signals
- **Flexible Data Sources**: Support for both live API data and local Excel files

## 📊 Trading Strategy

NiftyBot implements a dual-indicator strategy combining:

- **RSI (Relative Strength Index)**: Identifies overbought/oversold conditions
  - BUY when RSI < 30 (oversold)
  - SELL when RSI > 70 (overbought)

- **SMA Crossover**: Confirms trend direction
  - BUY when SMA20 > SMA50
  - SELL when SMA20 < SMA50

The system only generates signals when both indicators align, reducing false positives.

## 🛠️ Installation

### Prerequisites

- Python 3.8 or higher
- Google Cloud Service Account credentials
- Telegram Bot Token (optional)

### Setup Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd niftybot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure API credentials**
   - Place your Google Cloud credentials file as `capable-asset-468407-h9-dbda93abc544.json`
   - Update `config.py` with your API keys and settings

4. **Set up Telegram Bot (optional)**
   - Create a bot using [@BotFather](https://t.me/botfather)
   - Add your bot token and chat ID to `alerts.py`

## ⚙️ Configuration

Key settings in `config.py`:

```python

# Strategy parameters
RSI_WINDOW = 14
RSI_BUY_THRESHOLD = 30
RSI_SELL_THRESHOLD = 70
SHORT_MA_WINDOW = 20
LONG_MA_WINDOW = 50

# Backtesting
INITIAL_CAPITAL = 100000
```

## 🎯 Usage

### Basic Usage

Run the trading system with default settings:
```bash
python main.py
```

### Advanced Usage

**🎯 Recommended - Full Pipeline Test:**
```bash
python main.py --use-dummy --backtest --use-ml --use-telegram
```
This command runs the complete system with dummy data for safe testing, including backtesting, ML predictions, and Telegram alerts.

**Run with backtesting and ML predictions:**
```bash
python main.py --backtest --use-ml
```

**Run with Telegram alerts:**
```bash
python main.py --use-telegram
```

**Custom symbols and timeframe:**
```bash
python main.py --symbols RELIANCE.NS TCS.NS --time-frame 1d --period 6mo
```

**Use local Excel data instead of API:**
```bash
python main.py --use-dummy
```

### Command Line Arguments

| Argument | Description | Example |
|----------|-------------|---------|
| `--use-ml` | Enable machine learning predictions | `--use-ml` |
| `--use-telegram` | Send alerts to Telegram | `--use-telegram` |
| `--backtest` | Run backtesting on historical data | `--backtest` |
| `--symbols` | Custom stock symbols | `--symbols RELIANCE.NS TCS.NS` |
| `--time-frame` | Data interval (1d, 15m) | `--time-frame 1d` |
| `--period` | Historical period (6mo, 1y) | `--period 1y` |
| `--use-dummy` | Use local Excel data | `--use-dummy` |

## 📈 Data Flow

1. **Data Fetching**: Retrieves historical stock data from Yahoo Finance
2. **Indicator Calculation**: Computes RSI, SMA20, and SMA50
3. **Strategy Application**: Generates BUY/SELL/HOLD signals
4. **Backtesting**: Tests strategy performance (optional)
5. **ML Predictions**: Generates next-day predictions (optional)
6. **Logging**: Records results to Google Sheets
7. **Alerts**: Sends notifications via Telegram (optional)

## 📊 Google Sheets Integration

The system automatically logs data to three sheets:

- **Trade Log**: Detailed transaction records
- **P&L**: Profit and loss calculations
- **Summary**: Performance metrics and ML accuracy

## 🔧 Development

### Project Structure

```
niftybot-0/
├── main.py              # Main orchestrator
├── config.py            # Configuration settings
├── data_fetcher.py      # Data retrieval from APIs
├── indicators.py        # Technical indicator calculations
├── strategy.py          # Trading strategy implementation
├── backtest.py          # Backtesting engine
├── ml_model.py          # Machine learning predictions
├── google_sheets.py   # Google Sheets integration
├── alerts.py            # Telegram notifications
├── utils.py             # Utility functions
└── requirements.txt     # Python dependencies
```

### Adding New Indicators

1. Add indicator calculation in `indicators.py`
2. Update strategy logic in `strategy.py`
3. Test with backtesting before live deployment

### Adding New Symbols

Update the `TICKERS` list in `config.py`:
```python
TICKERS = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ITC.NS"]
```

## 🚨 Risk Disclaimer

This is an educational project for algorithmic trading concepts. **DO NOT use for live trading without proper testing and understanding of the risks involved.**

- Past performance does not guarantee future results
- Always test strategies thoroughly with backtesting
- Consider transaction costs and slippage in real trading
- Market conditions can change rapidly

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 📞 Support

For questions or support, please open an issue on GitHub or contact the development team.

---

**Happy Trading! 🎯**

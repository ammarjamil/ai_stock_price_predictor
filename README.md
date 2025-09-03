# CoinGecko Cryptocurrency Data Scraper

A comprehensive Python tool for fetching cryptocurrency data from CoinGecko API and generating AI-powered trading analysis insights.

## 🚀 Features

- **Real-time Data Fetching**: Get current prices, market cap, volume, and rankings
- **Historical Data**: Retrieve price history with customizable timeframes
- **Global Market Context**: Access overall cryptocurrency market statistics
- **Multiple Output Formats**: Console display, JSON export, CSV/Excel files
- **AI Trading Analysis**: Structured prompts for LLM-powered trading insights
- **Smart Coin Lookup**: Flexible search by coin name, symbol, or ID
- **Risk Management Focus**: Built-in position sizing and risk assessment tools

## 📋 Requirements

```bash
pip install requests pandas argparse openpyxl
```

## 🛠️ Installation

1. Clone or download the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the scraper:
   ```bash
   python coingecko_scraper.py --coin bitcoin --timeframe weekly
   ```

## 💻 Usage

### Basic Usage

```bash
# Get Bitcoin data for the past week
python coingecko_scraper.py --coin bitcoin --timeframe weekly

# Get Ethereum data for the past day
python coingecko_scraper.py --coin ethereum --timeframe daily

# Get Solana data for the past month
python coingecko_scraper.py --coin solana --timeframe monthly
```

### Advanced Usage

```bash
# Save data to Excel/CSV files
python coingecko_scraper.py --coin bitcoin --timeframe weekly --save-csv

# Get JSON output for API integration
python coingecko_scraper.py --coin ethereum --timeframe daily --json-output

# Custom output filename
python coingecko_scraper.py --coin bitcoin --timeframe weekly --save-csv --output-file my_bitcoin_analysis
```

### Command Line Options

| Option | Short | Description | Example |
|--------|-------|-------------|---------|
| `--coin` | `-c` | Coin name or symbol (required) | `bitcoin`, `btc`, `ethereum`, `eth` |
| `--timeframe` | `-t` | Data timeframe | `daily`, `weekly`, `monthly` |
| `--save-csv` | | Save results to CSV/Excel | |
| `--json-output` | | Output raw JSON data | |
| `--output-file` | `-o` | Custom filename | `my_analysis` |

## 📊 Data Output

### Console Output
Rich formatted display including:
- 💰 Current market data (price, market cap, volume)
- 🏦 Supply information (circulating, total, max supply)
- 📊 Price changes (24h, 7d, 30d)
- 🏆 All-time records (ATH, ATL)
- 🌍 Global market statistics
- ⏰ Recent price history

### JSON Output
Structured data perfect for API integration:
```json
{
  "coin_id": "bitcoin",
  "name": "Bitcoin",
  "symbol": "BTC",
  "current_price": 61234.56,
  "market_cap": 1203456789012,
  "volume_24h": 23456789012,
  "historical_prices": [...],
  "global_market_data": {...}
}
```

### File Exports
- **Excel (.xlsx)**: Multi-sheet workbook with current data and historical prices
- **CSV (.csv)**: Current market data in comma-separated format

## 🤖 AI Trading Analysis Integration

### LLM Prompt Template

Use the included prompt template to get AI-powered trading insights:

```python
prompt = """You are a professional cryptocurrency trading analyst AI...
Data: {coin_data}
Analyze this cryptocurrency data and provide your response in JSON format..."""

# Get coin data
coin_data = scraper.scrape_coin_data("bitcoin", "weekly")

# Format prompt
analysis_prompt = prompt.format(coin_data=json.dumps(coin_data))

# Send to your preferred LLM (ChatGPT, Claude, etc.)
```

### AI Analysis Output

The AI analysis provides:
- **Market Analysis**: Trend direction, confidence levels, market phase
- **Trading Zones**: Buy/sell zones with technical reasoning
- **Take Profit Levels**: TP1, TP2, TP3 with probabilities
- **Stop Loss Recommendations**: Conservative and moderate levels
- **Technical Indicators**: RSI, MACD, volume analysis
- **Risk Management**: Position sizing and risk warnings
- **Time Horizon Analysis**: Short, medium, long-term outlooks

## 📈 Example Workflows

### 1. Quick Market Check
```bash
python coingecko_scraper.py --coin bitcoin --timeframe daily
```

### 2. Detailed Analysis with Export
```bash
python coingecko_scraper.py --coin ethereum --timeframe weekly --save-csv --output-file eth_analysis
```

### 3. AI Trading Analysis
```bash
# Get JSON data
python coingecko_scraper.py --coin solana --timeframe weekly --json-output > solana_data.json

# Use the data with AI prompt template for trading insights
```

### 4. Portfolio Monitoring
```bash
# Monitor multiple coins
python coingecko_scraper.py --coin bitcoin --timeframe weekly --save-csv
python coingecko_scraper.py --coin ethereum --timeframe weekly --save-csv  
python coingecko_scraper.py --coin solana --timeframe weekly --save-csv
```

## 🔧 Configuration

### VS Code Debug Configuration (launch.json)
```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "CoinGecko Scraper - Bitcoin Weekly",
            "type": "debugpy",
            "request": "launch",
            "program": "${workspaceFolder}/coingecko_scraper.py",
            "args": ["--coin", "bitcoin", "--timeframe", "weekly"],
            "console": "integratedTerminal",
            "cwd": "${workspaceFolder}"
        }
    ]
}
```

## 📚 API Reference

### CoinGeckoAPIScraper Class

#### Methods

- `get_coin_id(coin_input)`: Convert coin name/symbol to CoinGecko ID
- `get_current_data(coin_id)`: Fetch current market data
- `get_historical_data(coin_id, timeframe)`: Get historical price data
- `scrape_coin_data(coin_input, timeframe)`: Main method for complete data collection

#### Data Fields

**Current Market Data:**
- `current_price`: Current USD price
- `market_cap`: Market capitalization
- `volume_24h`: 24-hour trading volume
- `market_cap_rank`: Market cap ranking
- `price_change_24h/7d/30d`: Price change percentages

**Supply Information:**
- `circulating_supply`: Coins in circulation
- `total_supply`: Total coins created
- `max_supply`: Maximum possible supply

**Historical Data:**
- `timestamp`: Unix timestamp
- `date`: Human-readable date
- `price`: Historical price
- `volume`: Historical volume
- `market_cap`: Historical market cap

## 🚨 Rate Limiting & Best Practices

- **API Limits**: CoinGecko free tier allows ~10-30 requests per minute
- **Built-in Delays**: Automatic delays between requests
- **Respectful Usage**: Don't spam the API with rapid requests
- **Error Handling**: Comprehensive error handling and retry logic

## ⚠️ Disclaimers

- **Educational Purpose Only**: This tool is for educational and research purposes
- **Not Financial Advice**: Do not use as sole basis for investment decisions
- **Market Risk**: Cryptocurrency markets are highly volatile and risky
- **API Dependency**: Relies on CoinGecko API availability and accuracy
- **DYOR**: Always do your own research before making investment decisions

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues, feature requests, or pull requests.

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🔗 Links

- [CoinGecko API Documentation](https://www.coingecko.com/en/api/documentation)
- [Pandas Documentation](https://pandas.pydata.org/docs/)
- [Requests Documentation](https://docs.python-requests.org/)

## 📞 Support

If you encounter any issues or have questions:
1. Check the existing issues on GitHub
2. Create a new issue with detailed description
3. Include error messages and system information

---

**Happy Trading! 🚀📈**

*Remember: Always trade responsibly and never invest more than you can afford to lose.*
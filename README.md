# AI Stock Price Predictor

A comprehensive Python tool for fetching cryptocurrency data from CoinGecko API and generating AI-powered trading analysis insights using Groq LLM integration.

## 🚀 Features

- **Real-time Data Fetching**: Get current prices, market cap, volume, and rankings
- **Historical Data**: Retrieve price history with customizable timeframes
- **Global Market Context**: Access overall cryptocurrency market statistics
- **Multiple Output Formats**: Console display, JSON export, CSV/Excel files
- **AI Trading Analysis**: Integrated Groq LLM analysis for comprehensive trading insights
- **Smart Coin Lookup**: Flexible search by coin name, symbol, or ID
- **Risk Management Focus**: Built-in position sizing and risk assessment tools

## 📋 Requirements

```bash
pip install -r requirements.txt
```

**Dependencies include:**
- `requests`, `pandas` - Data fetching and processing
- `langchain-groq`, `langchain` - LLM integration for AI analysis
- `python-dotenv` - Environment variable management
- `argparse` - CLI interface

## 🛠️ Installation

1. Clone or download the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up environment variables:
   ```bash
   # Create .env file with:
   GROQ_API_KEY=your_groq_api_key_here
   GROQ_MODEL=openai/gpt-oss-20b
   DEBUG=true
   ```
4. Run the application:
   ```bash
   python main.py --coin bitcoin --timeframe weekly
   ```

## 💻 Usage

### Basic Usage

```bash
# Get Bitcoin data with AI analysis
python main.py --coin bitcoin --timeframe weekly

# Get Ethereum data for the past day
python main.py --coin ethereum --timeframe daily

# Get Solana data for the past month
python main.py --coin solana --timeframe monthly
```

### Advanced Usage

```bash
# Save data to Excel/CSV files
python main.py --coin bitcoin --timeframe weekly --save-csv

# Get JSON output for API integration (skips AI analysis)
python main.py --coin ethereum --timeframe daily --json-output

# Custom output filename
python main.py --coin bitcoin --timeframe weekly --save-csv --output-file my_bitcoin_analysis
```

### Command Line Options

| Option          | Short | Description                    | Example                             |
| --------------- | ----- | ------------------------------ | ----------------------------------- |
| `--coin`        | `-c`  | Coin name or symbol (required) | `bitcoin`, `btc`, `ethereum`, `eth` |
| `--timeframe`   | `-t`  | Data timeframe                 | `daily`, `weekly`, `monthly`        |
| `--save-csv`    |       | Save results to CSV/Excel      |                                     |
| `--json-output` |       | Output raw JSON data           |                                     |
| `--output-file` | `-o`  | Custom filename                | `my_analysis`                       |

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

The application automatically provides AI-powered trading analysis using Groq LLM integration.

### Configuration

```bash
# Required environment variables in .env:
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=openai/gpt-oss-20b  # or your preferred model
DEBUG=true  # saves prompt.txt and response.txt files
```

### How It Works

1. **Data Collection**: Fetches current and historical cryptocurrency data
2. **Data Formatting**: Structures data for analysis
3. **AI Analysis**: Automatically sends formatted data to Groq LLM
4. **Insights Generation**: Receives comprehensive trading analysis

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

### 1. Quick Market Check with AI Analysis

```bash
python main.py --coin bitcoin --timeframe daily
```

### 2. Detailed Analysis with Export

```bash
python main.py --coin ethereum --timeframe weekly --save-csv --output-file eth_analysis
```

### 3. JSON Data Only (Skip AI Analysis)

```bash
# Get raw JSON data without AI analysis
python main.py --coin solana --timeframe weekly --json-output > solana_data.json
```

### 4. Portfolio Monitoring

```bash
# Monitor multiple coins with AI insights
python main.py --coin bitcoin --timeframe weekly --save-csv
python main.py --coin ethereum --timeframe weekly --save-csv
python main.py --coin solana --timeframe weekly --save-csv
```

## 🔧 Configuration

### VS Code Debug Configuration (launch.json)

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "AI Stock Predictor - Bitcoin Weekly",
      "type": "debugpy",
      "request": "launch",
      "program": "${workspaceFolder}/main.py",
      "args": ["--coin", "bitcoin", "--timeframe", "weekly"],
      "console": "integratedTerminal",
      "cwd": "${workspaceFolder}",
      "envFile": "${workspaceFolder}/.env"
    }
  ]
}
```

## 📚 API Reference

### Core Components

#### CoinGeckoAPIScraper Class (data/coingecko_scraper.py)

**Methods:**
- `get_coin_id(coin_input)`: Convert coin name/symbol to CoinGecko ID
- `get_current_data(coin_id)`: Fetch current market data
- `get_historical_data(coin_id, timeframe)`: Get historical price data
- `scrape_coin_data(coin_input, timeframe)`: Main method for complete data collection

#### LLMService Class (service/llm_service.py)

**Methods:**
- `__init__(model)`: Initialize with Groq LLM
- `analyze_coin(coin_data)`: Perform AI analysis on cryptocurrency data

#### Output Formatter (utils/output_formatter.py)

**Functions:**
- `print_formatted_output(data)`: Rich console formatting for market data

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

### CoinGecko API
- **API Limits**: CoinGecko free tier allows ~10-30 requests per minute
- **Built-in Delays**: Automatic delays between requests
- **Respectful Usage**: Don't spam the API with rapid requests
- **Error Handling**: Comprehensive error handling and retry logic

### Groq LLM API
- **API Key Required**: Set `GROQ_API_KEY` in `.env` file
- **Model Selection**: Configure via `GROQ_MODEL` environment variable
- **Rate Limits**: Respect Groq API rate limits for your tier

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

_Remember: Always trade responsibly and never invest more than you can afford to lose._

# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a CoinGecko cryptocurrency data scraper with AI-powered trading analysis. The application fetches cryptocurrency data from CoinGecko API and generates LLM-powered trading insights using Groq API.

## Development Commands

### Running the Application
```bash
# Basic usage
python main.py --coin bitcoin --timeframe weekly

# Save to CSV/Excel
python main.py --coin ethereum --timeframe daily --save-csv

# JSON output only
python main.py --coin solana --timeframe monthly --json-output

# Custom output filename
python main.py --coin bitcoin --timeframe weekly --save-csv --output-file my_analysis
```

### Environment Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Environment variables required in .env:
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=openai/gpt-oss-20b  # or preferred model
DEBUG=true  # enables prompt/response file output
```

### Testing
No specific test framework is configured. Manual testing is done through running the main script with different coin parameters.

## Architecture

### Core Components

**main.py**: Entry point with CLI argument parsing and orchestration
- Initializes `CoinGeckoAPIScraper` for data fetching
- Uses `LLMService` for AI analysis 
- Handles output formatting and file exports

**data/coingecko_scraper.py**: CoinGecko API integration
- `CoinGeckoAPIScraper` class handles all API interactions
- Methods: `get_coin_id()`, `get_current_data()`, `get_historical_data()`, `scrape_coin_data()`
- Built-in rate limiting and error handling

**service/llm_service.py**: LLM analysis service
- `LLMService` class wraps Groq API integration using LangChain
- Uses prompt template from `template/prompt_template_new.py`
- Configurable model selection via environment variables

**utils/output_formatter.py**: Console output formatting
- `print_formatted_output()` creates rich console displays
- Formats current prices, market data, supply info, price changes, historical data

**template/prompt_template_new.py**: LLM prompt template
- Contains the structured prompt for cryptocurrency trading analysis
- Used by LLMService for consistent AI analysis format

### Data Flow

1. CLI arguments parsed in main.py
2. CoinGeckoAPIScraper fetches current + historical data
3. Data formatted for console output
4. LLMService analyzes formatted data using prompt template
5. Optional CSV/Excel export if requested

### Configuration

- **API Keys**: Groq API key required in `.env` file
- **Debug Mode**: When `DEBUG=true`, saves prompt.txt and response.txt files
- **Rate Limiting**: Built into CoinGecko API interactions
- **Timeframes**: Supports daily, weekly, monthly historical data

### Dependencies

Key packages:
- `requests`, `pandas`: Data fetching and processing
- `langchain-groq`, `langchain`: LLM integration
- `python-dotenv`: Environment variable management
- `argparse`: CLI interface

### File Structure

```
├── main.py                    # Entry point
├── data/
│   └── coingecko_scraper.py   # API scraper
├── service/
│   └── llm_service.py         # LLM integration  
├── utils/
│   └── output_formatter.py    # Console output
├── template/
│   └── prompt_template_new.py # LLM prompt
├── requirements.txt
└── .env                       # API keys/config
```
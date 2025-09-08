#!/usr/bin/env python3
"""
CoinGecko API Cryptocurrency Data Scraper

A Python script that fetches cryptocurrency data from CoinGecko API.
Supports fetching current prices, market data, and historical price charts.

Requirements:
    pip install requests pandas argparse

Usage:
    python coingecko_scraper.py --coin bitcoin --timeframe weekly
    python coingecko_scraper.py --coin ethereum --timeframe daily --save-csv
"""

import requests
import json
import argparse
import pandas as pd
from datetime import datetime, timedelta
import time
import sys
from typing import Dict, List, Optional
from langchain.prompts import PromptTemplate
from template.prompt_template_new import prompt
from dotenv import load_dotenv
from langchain_groq import ChatGroq
import os
from service.llm_service import LLMService
from data.coingecko_scraper import CoinGeckoAPIScraper
from utils.output_formatter import print_formatted_output
load_dotenv()



llm_service = LLMService(model="openai/gpt-oss-20b")  # Using your preferred model

def main():
    """Main function to run the scraper."""
    parser = argparse.ArgumentParser(
        description='CoinGecko API Cryptocurrency Data Scraper',
        epilog='''
Examples:
  python coingecko_scraper.py --coin bitcoin --timeframe weekly
  python coingecko_scraper.py --coin eth --timeframe daily --save-csv
  python coingecko_scraper.py --coin solana --timeframe monthly --json-output
        ''',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--coin', '-c', required=True, 
                       help='Coin name or symbol (e.g., bitcoin, btc, ethereum, eth, solana, sol)')
    parser.add_argument('--timeframe', '-t', choices=['daily', 'weekly', 'monthly'], 
                       default='weekly', 
                       help='Timeframe for historical data (default: weekly)')
    parser.add_argument('--save-csv', action='store_true', 
                       help='Save results to CSV/Excel files')
    parser.add_argument('--json-output', action='store_true', 
                       help='Output raw JSON data instead of formatted display')
    parser.add_argument('--output-file', '-o', 
                       help='Custom output filename (without extension)')
    
    args = parser.parse_args()
    
    # Initialize scraper
    scraper = CoinGeckoAPIScraper()
    
    try:
        # Scrape data
        data = scraper.scrape_coin_data(args.coin, args.timeframe)
        
        if not data:
            print("❌ Failed to scrape coin data")
            sys.exit(1)
        
        # Output data
        if args.json_output:
            print(json.dumps(data, indent=2, default=str))
        else:
            final_data= print_formatted_output(data)
            llm_service.analyze_coin(final_data)
           
        
        # Save to file if requested
        if args.save_csv:
            filename = args.output_file or f"{data['coin_id']}_{args.timeframe}_data"
            save_to_csv(data, filename)
        
    except KeyboardInterrupt:
        print("\n⏹️  Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
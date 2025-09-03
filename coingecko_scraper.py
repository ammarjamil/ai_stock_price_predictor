#!/usr/bin/env python3
"""
CoinGecko Cryptocurrency Data Scraper

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


class CoinGeckoScraper:
    """
    A scraper class for fetching cryptocurrency data from CoinGecko API.
    """
    
    def __init__(self):
        self.base_url = "https://api.coingecko.com/api/v3"
        self.session = requests.Session()
        # Add headers to avoid rate limiting
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def get_coin_id(self, coin_input: str) -> Optional[str]:
        """
        Convert coin name or symbol to CoinGecko coin ID.
        
        Args:
            coin_input: Coin name or symbol (e.g., 'bitcoin', 'btc')
            
        Returns:
            CoinGecko coin ID or None if not found
        """
        try:
            # First, try to get coins list
            url = f"{self.base_url}/coins/list"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            coins = response.json()
            coin_input_lower = coin_input.lower()
            
            # Search by ID, name, or symbol
            for coin in coins:
                if (coin['id'].lower() == coin_input_lower or 
                    coin['name'].lower() == coin_input_lower or 
                    coin['symbol'].lower() == coin_input_lower):
                    return coin['id']
            
            return None
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching coins list: {e}")
            return None
    
    def get_current_data(self, coin_id: str) -> Optional[Dict]:
        """
        Fetch current market data for a cryptocurrency.
        
        Args:
            coin_id: CoinGecko coin ID
            
        Returns:
            Dictionary containing current market data
        """
        try:
            url = f"{self.base_url}/coins/{coin_id}"
            params = {
                'localization': 'false',
                'tickers': 'false',
                'market_data': 'true',
                'community_data': 'false',
                'developer_data': 'false',
                'sparkline': 'false'
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            market_data = data['market_data']
            
            return {
                'coin_id': coin_id,
                'name': data['name'],
                'symbol': data['symbol'].upper(),
                'current_price': market_data['current_price']['usd'],
                'market_cap': market_data['market_cap']['usd'],
                'volume_24h': market_data['total_volume']['usd'],
                'price_change_24h': market_data['price_change_percentage_24h'],
                'price_change_7d': market_data['price_change_percentage_7d'],
                'price_change_30d': market_data['price_change_percentage_30d'],
                'last_updated': market_data['last_updated']
            }
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching current data: {e}")
            return None
        except KeyError as e:
            print(f"Error parsing market data: {e}")
            return None
    
    def get_historical_data(self, coin_id: str, timeframe: str) -> List[Dict]:
        """
        Fetch historical price data for a cryptocurrency.
        
        Args:
            coin_id: CoinGecko coin ID
            timeframe: 'daily', 'weekly', or 'monthly'
            
        Returns:
            List of dictionaries containing historical price data
        """
        try:
            # Determine days parameter based on timeframe
            days_map = {
                'daily': 1,
                'weekly': 7,
                'monthly': 30
            }
            
            days = days_map.get(timeframe, 7)
            
            url = f"{self.base_url}/coins/{coin_id}/market_chart"
            params = {
                'vs_currency': 'usd',
                'days': days,
                'interval': 'hourly' if days <= 7 else 'daily'
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            prices = data['prices']
            
            historical_data = []
            for timestamp, price in prices:
                date = datetime.fromtimestamp(timestamp / 1000).strftime('%Y-%m-%d %H:%M:%S')
                historical_data.append({
                    'timestamp': timestamp,
                    'date': date,
                    'price': round(price, 6)
                })
            
            return historical_data
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching historical data: {e}")
            return []
        except KeyError as e:
            print(f"Error parsing historical data: {e}")
            return []
    
    def scrape_coin_data(self, coin_input: str, timeframe: str) -> Optional[Dict]:
        """
        Main method to scrape all coin data.
        
        Args:
            coin_input: Coin name or symbol
            timeframe: 'daily', 'weekly', or 'monthly'
            
        Returns:
            Complete coin data dictionary
        """
        print(f"Fetching data for: {coin_input}")
        
        # Get coin ID
        coin_id = self.get_coin_id(coin_input)
        if not coin_id:
            print(f"Could not find coin: {coin_input}")
            return None
        
        print(f"Found coin ID: {coin_id}")
        
        # Get current market data
        current_data = self.get_current_data(coin_id)
        if not current_data:
            print("Failed to fetch current market data")
            return None
        
        # Add small delay to respect rate limits
        time.sleep(1)
        
        # Get historical data
        historical_data = self.get_historical_data(coin_id, timeframe)
        
        # Combine all data
        result = {
            **current_data,
            'timeframe': timeframe,
            'historical_prices': historical_data,
            'data_points': len(historical_data),
            'scraped_at': datetime.now().isoformat()
        }
        
        return result


def save_to_csv(data: Dict, filename: str):
    """Save coin data to CSV file."""
    try:
        # Create main data DataFrame
        main_data = {
            'Coin': data['name'],
            'Symbol': data['symbol'],
            'Current Price (USD)': data['current_price'],
            'Market Cap (USD)': data['market_cap'],
            '24h Volume (USD)': data['volume_24h'],
            '24h Change (%)': data['price_change_24h'],
            '7d Change (%)': data['price_change_7d'],
            '30d Change (%)': data['price_change_30d'],
            'Timeframe': data['timeframe'],
            'Last Updated': data['last_updated']
        }
        
        main_df = pd.DataFrame([main_data])
        
        # Create historical data DataFrame
        if data['historical_prices']:
            historical_df = pd.DataFrame(data['historical_prices'])
        else:
            historical_df = pd.DataFrame()
        
        # Save to Excel with multiple sheets
        excel_filename = filename.replace('.csv', '.xlsx')
        with pd.ExcelWriter(excel_filename, engine='openpyxl') as writer:
            main_df.to_excel(writer, sheet_name='Current Data', index=False)
            if not historical_df.empty:
                historical_df.to_excel(writer, sheet_name='Historical Prices', index=False)
        
        print(f"Data saved to: {excel_filename}")
        
    except Exception as e:
        print(f"Error saving to file: {e}")


def print_formatted_output(data: Dict):
    """Print data in a formatted manner."""
    print("\n" + "="*60)
    print(f"CRYPTOCURRENCY DATA: {data['name']} ({data['symbol']})")
    print("="*60)
    
    print(f"Current Price:        ${data['current_price']:,.2f}")
    print(f"Market Cap:           ${data['market_cap']:,}")
    print(f"24h Trading Volume:   ${data['volume_24h']:,}")
    
    print(f"\nPrice Changes:")
    print(f"  24h:                {data['price_change_24h']:+.2f}%")
    print(f"  7d:                 {data['price_change_7d']:+.2f}%")
    print(f"  30d:                {data['price_change_30d']:+.2f}%")
    
    print(f"\nTimeframe:            {data['timeframe']}")
    print(f"Historical Data Points: {data['data_points']}")
    print(f"Last Updated:         {data['last_updated']}")
    print(f"Scraped At:           {data['scraped_at']}")
    
    if data['historical_prices']:
        print(f"\nRecent Price History (last 5 entries):")
        for entry in data['historical_prices'][-5:]:
            print(f"  {entry['date']}: ${entry['price']:,.6f}")


def main():
    """Main function to run the scraper."""
    parser = argparse.ArgumentParser(description='CoinGecko Cryptocurrency Data Scraper')
    parser.add_argument('--coin', '-c', required=True, 
                       help='Coin name or symbol (e.g., bitcoin, btc, ethereum)')
    parser.add_argument('--timeframe', '-t', choices=['daily', 'weekly', 'monthly'], 
                       default='weekly', help='Timeframe for historical data')
    parser.add_argument('--save-csv', action='store_true', 
                       help='Save results to CSV/Excel file')
    parser.add_argument('--json-output', action='store_true', 
                       help='Output raw JSON data')
    parser.add_argument('--output-file', '-o', 
                       help='Custom output filename (without extension)')
    
    args = parser.parse_args()
    
    # Initialize scraper
    scraper = CoinGeckoScraper()
    
    # Scrape data
    try:
        data = scraper.scrape_coin_data(args.coin, args.timeframe)
        
        if not data:
            print("Failed to scrape coin data")
            sys.exit(1)
        
        # Output data
        if args.json_output:
            print(json.dumps(data, indent=2))
        else:
            print_formatted_output(data)
        
        # Save to file if requested
        if args.save_csv:
            filename = args.output_file or f"{data['coin_id']}_{args.timeframe}_data"
            if not filename.endswith('.csv'):
                filename += '.csv'
            save_to_csv(data, filename)
        
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
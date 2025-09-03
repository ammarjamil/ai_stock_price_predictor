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
load_dotenv()

class LLMService:
    """Service for LLM-powered analysis"""

    def __init__(self, model: str = "openai/gpt-oss-20b"):
        """Initialize the system with Groq LLM"""
        try:
            self.model = model
            self.llm = ChatGroq(api_key=os.getenv("GROQ_API_KEY"), model_name=model, temperature=0.3)
            print(f"Initialized with model: {model}")
        except Exception as e:
            raise Exception(f"Failed to initialize Groq model '{model}': {e}")
        
        # Create a more focused prompt template
        self.prompt_template = PromptTemplate(
            input_variables=["coin_data"],
            template=prompt
        )

    def analyze_coin(self, coin_data: str) -> dict:
        """Analyze news using Groq LLM"""
        try:
            # prompt = self.create_analysis_prompt(headline, content, symbol)
            formatted_prompt = self.prompt_template.format(coin_data=coin_data)

            if(os.getenv("DEBUG").lower() == "true"):
                with open("prompt.txt", "w", encoding="utf-8") as f:
                    f.write(formatted_prompt)
            response = self.llm.invoke(formatted_prompt)

            print(f"Received response, length: {len(response.content)} characters")
            if(os.getenv("DEBUG").lower() == "true"):
                with open("response.txt", "w", encoding="utf-8") as ff:
                    ff.write(response.content)
                
            # # Parse JSON response
            # response_text = json.loads(json_str)
            return True
        
                
        except Exception as e:
            print(f"LLM analysis error: {e}")
            return False



class CoinGeckoAPIScraper:
    """
    A scraper class for fetching cryptocurrency data from CoinGecko API.
    """
    
    def __init__(self):
        self.base_url = "https://api.coingecko.com/api/v3"
        self.session = requests.Session()
        
        # Add headers to avoid rate limiting
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9'
        })
        
        # Configure session
        self.session.timeout = 30
        print("CoinGecko API Scraper initialized")
    
    def get_coin_id(self, coin_input: str) -> Optional[str]:
        """
        Convert coin name or symbol to CoinGecko coin ID.
        
        Args:
            coin_input: Coin name or symbol (e.g., 'bitcoin', 'btc')
            
        Returns:
            CoinGecko coin ID or None if not found
        """
        try:
            print(f"Looking up coin ID for: {coin_input}")
            
            # First, try to get coins list with search
            url = f"{self.base_url}/search"
            params = {'query': coin_input}
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                search_data = response.json()
                
                # Check coins in search results
                for coin in search_data.get('coins', []):
                    if (coin['id'].lower() == coin_input.lower() or 
                        coin['name'].lower() == coin_input.lower() or 
                        coin['symbol'].lower() == coin_input.lower()):
                        print(f"✓ Found coin ID: {coin['id']}")
                        return coin['id']
                
                # If exact match not found, return first result if available
                if search_data.get('coins'):
                    first_match = search_data['coins'][0]
                    print(f"✓ Using closest match: {first_match['id']} ({first_match['name']})")
                    return first_match['id']
            
            # Fallback: try getting full coins list (rate limited approach)
            print("Searching in full coins list...")
            url = f"{self.base_url}/coins/list"
            response = self.session.get(url, timeout=15)
            
            if response.status_code == 200:
                coins = response.json()
                coin_input_lower = coin_input.lower()
                
                # Search by ID, name, or symbol
                for coin in coins:
                    if (coin['id'].lower() == coin_input_lower or 
                        coin['name'].lower() == coin_input_lower or 
                        coin['symbol'].lower() == coin_input_lower):
                        print(f"✓ Found coin ID: {coin['id']}")
                        return coin['id']
            
            print(f"❌ Could not find coin: {coin_input}")
            return None
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching coin ID: {e}")
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
            print(f"Fetching current market data for: {coin_id}")
            
            url = f"{self.base_url}/coins/{coin_id}"
            params = {
                'localization': 'false',
                'tickers': 'false',
                'market_data': 'true',
                'community_data': 'false',
                'developer_data': 'false',
                'sparkline': 'false'
            }
            
            response = self.session.get(url, params=params, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            market_data = data.get('market_data', {})
            
            # Extract data with safe navigation
            current_data = {
                'coin_id': coin_id,
                'name': data.get('name', 'Unknown'),
                'symbol': data.get('symbol', 'Unknown').upper(),
                'current_price': market_data.get('current_price', {}).get('usd', 0),
                'market_cap': market_data.get('market_cap', {}).get('usd', 0),
                'volume_24h': market_data.get('total_volume', {}).get('usd', 0),
                'price_change_24h': market_data.get('price_change_percentage_24h', 0),
                'price_change_7d': market_data.get('price_change_percentage_7d', 0),
                'price_change_30d': market_data.get('price_change_percentage_30d', 0),
                'circulating_supply': market_data.get('circulating_supply', 0),
                'total_supply': market_data.get('total_supply', 0),
                'max_supply': market_data.get('max_supply', 0),
                'ath': market_data.get('ath', {}).get('usd', 0),
                'atl': market_data.get('atl', {}).get('usd', 0),
                'market_cap_rank': data.get('market_cap_rank', 0),
                'last_updated': market_data.get('last_updated', datetime.now().isoformat())
            }
            
            print(f"✓ Current price: ${current_data['current_price']:,.2f}")
            print(f"✓ Market cap: ${current_data['market_cap']:,}")
            print(f"✓ 24h volume: ${current_data['volume_24h']:,}")
            
            return current_data
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching current data: {e}")
            return None
        except KeyError as e:
            print(f"❌ Error parsing market data: {e}")
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
            print(f"Fetching historical data for {timeframe} timeframe...")
            
            # Determine days parameter based on timeframe
            timeframe_config = {
                'daily': {'days': 1, 'interval': 'hourly'},
                'weekly': {'days': 7, 'interval': 'hourly'},
                'monthly': {'days': 30, 'interval': 'daily'}
            }
            
            config = timeframe_config.get(timeframe, timeframe_config['weekly'])
            
            url = f"{self.base_url}/coins/{coin_id}/market_chart"
            params = {
                'vs_currency': 'usd',
                'days': config['days'],
                'interval': config['interval']
            }
            
            response = self.session.get(url, params=params, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            prices = data.get('prices', [])
            volumes = data.get('total_volumes', [])
            market_caps = data.get('market_caps', [])
            
            historical_data = []
            
            # Combine price, volume, and market cap data
            for i, (timestamp, price) in enumerate(prices):
                date = datetime.fromtimestamp(timestamp / 1000)
                
                # Get corresponding volume and market cap
                volume = volumes[i][1] if i < len(volumes) else 0
                market_cap = market_caps[i][1] if i < len(market_caps) else 0
                
                historical_data.append({
                    'timestamp': timestamp,
                    'date': date.strftime('%Y-%m-%d %H:%M:%S'),
                    'price': round(price, 8),
                    'volume': round(volume, 2),
                    'market_cap': round(market_cap, 2)
                })
            
            print(f"✓ Retrieved {len(historical_data)} historical data points")
            return historical_data
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching historical data: {e}")
            return []
        except KeyError as e:
            print(f"❌ Error parsing historical data: {e}")
            return []
    
    def get_price_alerts_data(self, coin_id: str) -> Dict:
        """
        Get additional market data and statistics.
        
        Args:
            coin_id: CoinGecko coin ID
            
        Returns:
            Dictionary with additional market statistics
        """
        try:
            # Get global market data
            global_url = f"{self.base_url}/global"
            response = self.session.get(global_url, timeout=10)
            
            if response.status_code == 200:
                global_data = response.json().get('data', {})
                
                return {
                    'total_market_cap_usd': global_data.get('total_market_cap', {}).get('usd', 0),
                    'total_volume_24h_usd': global_data.get('total_volume', {}).get('usd', 0),
                    'bitcoin_percentage': global_data.get('market_cap_percentage', {}).get('btc', 0),
                    'active_cryptocurrencies': global_data.get('active_cryptocurrencies', 0),
                    'markets': global_data.get('markets', 0)
                }
        except:
            pass
        
        return {}
    
    def scrape_coin_data(self, coin_input: str, timeframe: str) -> Optional[Dict]:
        """
        Main method to scrape all coin data using CoinGecko API.
        
        Args:
            coin_input: Coin name or symbol
            timeframe: 'daily', 'weekly', or 'monthly'
            
        Returns:
            Complete coin data dictionary
        """
        print(f"🚀 Starting data collection for: {coin_input}")
        print("=" * 50)
        
        # Get coin ID
        coin_id = self.get_coin_id(coin_input)
        if not coin_id:
            print(f"❌ Could not find coin: {coin_input}")
            print("💡 Try using the exact coin name or symbol (e.g., 'bitcoin', 'btc', 'ethereum', 'eth')")
            return None
        
        # Get current market data
        current_data = self.get_current_data(coin_id)
        if not current_data:
            print("❌ Failed to fetch current market data")
            return None
        
        # Add small delay to respect rate limits
        time.sleep(1)
        
        # Get historical data
        historical_data = self.get_historical_data(coin_id, timeframe)
        
        # Add small delay to respect rate limits
        time.sleep(0.5)
        
        # Get additional market data
        additional_data = self.get_price_alerts_data(coin_id)
        
        # Combine all data
        result = {
            **current_data,
            'timeframe': timeframe,
            'historical_prices': historical_data,
            'data_points': len(historical_data),
            'global_market_data': additional_data,
            'scraped_at': datetime.now().isoformat(),
            'data_source': 'CoinGecko API'
        }
        
        print("=" * 50)
        print("✅ Data collection completed successfully!")
        
        return result


def save_to_csv(data: Dict, filename: str):
    """Save coin data to CSV and Excel files."""
    try:
        # Create main data DataFrame
        main_data = {
            'Coin': data['name'],
            'Symbol': data['symbol'],
            'Current Price (USD)': data['current_price'],
            'Market Cap (USD)': data['market_cap'],
            '24h Volume (USD)': data['volume_24h'],
            'Market Cap Rank': data['market_cap_rank'],
            'Circulating Supply': data['circulating_supply'],
            'Total Supply': data['total_supply'],
            'Max Supply': data['max_supply'],
            '24h Change (%)': data['price_change_24h'],
            '7d Change (%)': data['price_change_7d'],
            '30d Change (%)': data['price_change_30d'],
            'All Time High (USD)': data['ath'],
            'All Time Low (USD)': data['atl'],
            'Timeframe': data['timeframe'],
            'Data Source': data['data_source'],
            'Last Updated': data['last_updated'],
            'Scraped At': data['scraped_at']
        }
        
        # Add global market data if available
        if data.get('global_market_data'):
            global_data = data['global_market_data']
            main_data.update({
                'Total Crypto Market Cap (USD)': global_data.get('total_market_cap_usd', 0),
                'Total 24h Volume (USD)': global_data.get('total_volume_24h_usd', 0),
                'Bitcoin Dominance (%)': global_data.get('bitcoin_percentage', 0),
                'Active Cryptocurrencies': global_data.get('active_cryptocurrencies', 0)
            })
        
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
        
        # Also save main data to CSV
        csv_filename = filename if filename.endswith('.csv') else f"{filename}.csv"
        main_df.to_csv(csv_filename, index=False)
        
        print(f"📁 Data saved to:")
        print(f"   📊 Excel: {excel_filename}")
        print(f"   📄 CSV: {csv_filename}")
        
    except Exception as e:
        print(f"❌ Error saving to file: {e}")


def print_formatted_output(data: Dict):
    """Print data in a formatted manner."""
    print("\n" + "="*70)
    print(f"📈 CRYPTOCURRENCY DATA: {data['name']} ({data['symbol']})")
    print("="*70)
    
    # Current Price Section
    print(f"💰 CURRENT MARKET DATA:")
    print(f"   Current Price:        ${data['current_price']:,.8f}")
    print(f"   Market Cap:           ${data['market_cap']:,}")
    print(f"   24h Trading Volume:   ${data['volume_24h']:,}")
    print(f"   Market Cap Rank:      #{data['market_cap_rank']}")
    
    # Supply Information
    print(f"\n🏦 SUPPLY INFORMATION:")
    print(f"   Circulating Supply:   {data['circulating_supply']:,}")
    print(f"   Total Supply:         {data['total_supply']:,}")
    print(f"   Max Supply:           {data['max_supply']:,}" if data['max_supply'] else "   Max Supply:           ∞")
    
    # Price Changes
    print(f"\n📊 PRICE CHANGES:")
    def format_change(value):
        return f"{value:+.2f}%" if value != 0 else "0.00%"
    
    print(f"   24h:                  {format_change(data['price_change_24h'])}")
    print(f"   7d:                   {format_change(data['price_change_7d'])}")
    print(f"   30d:                  {format_change(data['price_change_30d'])}")
    
    # All-Time Records
    print(f"\n🏆 ALL-TIME RECORDS:")
    print(f"   All-Time High:        ${data['ath']:,.8f}")
    print(f"   All-Time Low:         ${data['atl']:,.8f}")
    
    # Global Market Data
    if data.get('global_market_data'):
        global_data = data['global_market_data']
        print(f"\n🌍 GLOBAL MARKET DATA:")
        print(f"   Total Crypto Market Cap: ${global_data.get('total_market_cap_usd', 0):,}")
        print(f"   Total 24h Volume:     ${global_data.get('total_volume_24h_usd', 0):,}")
        print(f"   Bitcoin Dominance:    {global_data.get('bitcoin_percentage', 0):.2f}%")
        print(f"   Active Cryptocurrencies: {global_data.get('active_cryptocurrencies', 0):,}")
    
    # Metadata
    print(f"\n📋 METADATA:")
    print(f"   Timeframe:            {data['timeframe']}")
    print(f"   Historical Data Points: {data['data_points']}")
    print(f"   Data Source:          {data['data_source']}")
    print(f"   Last Updated:         {data['last_updated']}")
    print(f"   Scraped At:           {data['scraped_at']}")
    
    # Recent Historical Data Preview
    if data['historical_prices']:
        print(f"\n⏰ RECENT PRICE HISTORY (last 5 entries):")
        for entry in data['historical_prices'][-5:]:
            print(f"   {entry['date']}: ${entry['price']:,.8f}")
    
    print("="*70)
    return data

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
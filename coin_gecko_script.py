#!/usr/bin/env python3
"""
CoinGecko API Cryptocurrency Data Scraper

A Python script that fetches cryptocurrency data from CoinGecko API using pycoingecko.
Supports fetching current prices, market data, and historical price charts.

Requirements:
    pip install pycoingecko pandas argparse python-dotenv langchain-groq

Usage:
    python coingecko_scraper.py --coin bitcoin --timeframe weekly
    python coingecko_scraper.py --coin ethereum --timeframe daily --save-csv
"""

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
from pycoingecko import CoinGeckoAPI

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
        """Analyze coin data using Groq LLM"""
        try:
            formatted_prompt = self.prompt_template.format(coin_data=coin_data)

            if os.getenv("DEBUG", "").lower() == "true":
                with open("prompt.txt", "w", encoding="utf-8") as f:
                    f.write(formatted_prompt)
            
            response = self.llm.invoke(formatted_prompt)

            print(f"Received response, length: {len(response.content)} characters")
            if os.getenv("DEBUG", "").lower() == "true":
                with open("response.txt", "w", encoding="utf-8") as ff:
                    ff.write(response.content)
                
            return True
        
        except Exception as e:
            print(f"LLM analysis error: {e}")
            return False


class CoinGeckoAPIScraper:
    """
    A scraper class for fetching cryptocurrency data from CoinGecko API using pycoingecko.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the CoinGecko API client.
        
        Args:
            api_key: Optional CoinGecko API key for higher rate limits
        """
        try:
            # Initialize pycoingecko client
            if api_key:
                self.cg = CoinGeckoAPI(api_key=api_key)
                print("✓ CoinGecko API initialized with API key")
            else:
                self.cg = CoinGeckoAPI()
                print("✓ CoinGecko API initialized (free tier)")
        except Exception as e:
            print(f"❌ Failed to initialize CoinGecko API: {e}")
            raise
    
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
            
            # First, try search API
            search_results = self.cg.search(query=coin_input)
            
            # Check coins in search results
            for coin in search_results.get('coins', []):
                if (coin['id'].lower() == coin_input.lower() or 
                    coin['name'].lower() == coin_input.lower() or 
                    coin['symbol'].lower() == coin_input.lower()):
                    print(f"✓ Found coin ID: {coin['id']}")
                    return coin['id']
            
            # If exact match not found, return first result if available
            if search_results.get('coins'):
                first_match = search_results['coins'][0]
                print(f"✓ Using closest match: {first_match['id']} ({first_match['name']})")
                return first_match['id']
            
            # Fallback: try getting full coins list
            print("Searching in full coins list...")
            coins_list = self.cg.get_coins_list()
            coin_input_lower = coin_input.lower()
            
            # Search by ID, name, or symbol
            for coin in coins_list:
                if (coin['id'].lower() == coin_input_lower or 
                    coin['name'].lower() == coin_input_lower or 
                    coin['symbol'].lower() == coin_input_lower):
                    print(f"✓ Found coin ID: {coin['id']}")
                    return coin['id']
            
            print(f"❌ Could not find coin: {coin_input}")
            return None
            
        except Exception as e:
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
            
            # Get detailed coin data
            data = self.cg.get_coin_by_id(
                id=coin_id,
                localization=False,
                tickers=False,
                market_data=True,
                community_data=False,
                developer_data=False,
                sparkline=False
            )
            
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
                'price_change_1y': market_data.get('price_change_percentage_1y', 0),
                'circulating_supply': market_data.get('circulating_supply', 0),
                'total_supply': market_data.get('total_supply', 0),
                'max_supply': market_data.get('max_supply', 0),
                'ath': market_data.get('ath', {}).get('usd', 0),
                'ath_date': market_data.get('ath_date', {}).get('usd', ''),
                'atl': market_data.get('atl', {}).get('usd', 0),
                'atl_date': market_data.get('atl_date', {}).get('usd', ''),
                'market_cap_rank': data.get('market_cap_rank', 0),
                'fully_diluted_valuation': market_data.get('fully_diluted_valuation', {}).get('usd', 0),
                'last_updated': market_data.get('last_updated', datetime.now().isoformat())
            }
            
            print(f"✓ Current price: ${current_data['current_price']:,.2f}")
            print(f"✓ Market cap: ${current_data['market_cap']:,}")
            print(f"✓ 24h volume: ${current_data['volume_24h']:,}")
            
            return current_data
            
        except Exception as e:
            print(f"❌ Error fetching current data: {e}")
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
                'monthly': {'days': 30, 'interval': 'daily'},
                'quarterly': {'days': 90, 'interval': 'daily'},
                'yearly': {'days': 365, 'interval': 'daily'}
            }
            
            config = timeframe_config.get(timeframe, timeframe_config['weekly'])
            
            # Get market chart data using pycoingecko
            data = self.cg.get_coin_market_chart_by_id(
                id=coin_id,
                vs_currency='usd',
                days=config['days']
            )
            
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
            
        except Exception as e:
            print(f"❌ Error fetching historical data: {e}")
            return []
    
    def get_global_market_data(self) -> Dict:
        """
        Get global cryptocurrency market statistics.
        
        Returns:
            Dictionary with global market statistics
        """
        try:
            print("Fetching global market data...")
            global_data = self.cg.get_global()
            
            data = global_data.get('data', {})
            
            return {
                'total_market_cap_usd': data.get('total_market_cap', {}).get('usd', 0),
                'total_volume_24h_usd': data.get('total_volume', {}).get('usd', 0),
                'bitcoin_percentage': data.get('market_cap_percentage', {}).get('btc', 0),
                'ethereum_percentage': data.get('market_cap_percentage', {}).get('eth', 0),
                'active_cryptocurrencies': data.get('active_cryptocurrencies', 0),
                'upcoming_icos': data.get('upcoming_icos', 0),
                'ongoing_icos': data.get('ongoing_icos', 0),
                'ended_icos': data.get('ended_icos', 0),
                'markets': data.get('markets', 0),
                'market_cap_change_percentage_24h': data.get('market_cap_change_percentage_24h_usd', 0)
            }
        except Exception as e:
            print(f"❌ Error fetching global market data: {e}")
            return {}
    
    def get_trending_coins(self) -> List[Dict]:
        """
        Get currently trending coins.
        
        Returns:
            List of trending coins
        """
        try:
            trending_data = self.cg.get_search_trending()
            trending_coins = []
            
            for coin_data in trending_data.get('coins', []):
                coin = coin_data.get('item', {})
                trending_coins.append({
                    'id': coin.get('id', ''),
                    'name': coin.get('name', ''),
                    'symbol': coin.get('symbol', ''),
                    'market_cap_rank': coin.get('market_cap_rank', 0),
                    'price_btc': coin.get('price_btc', 0)
                })
            
            return trending_coins[:10]  # Top 10 trending
        except Exception as e:
            print(f"❌ Error fetching trending coins: {e}")
            return []
    
    def get_market_data_by_rank(self, limit: int = 250) -> List[Dict]:
        """
        Get top cryptocurrencies by market cap.
        
        Args:
            limit: Number of coins to fetch (default: 250, max: 250)
            
        Returns:
            List of top cryptocurrencies
        """
        try:
            print(f"Fetching top {limit} cryptocurrencies by market cap...")
            
            market_data = self.cg.get_coins_markets(
                vs_currency='usd',
                order='market_cap_desc',
                per_page=min(limit, 250),
                page=1,
                sparkline=False,
                price_change_percentage='1h,24h,7d,30d,1y'
            )
            
            return market_data
        except Exception as e:
            print(f"❌ Error fetching market data: {e}")
            return []
    
    def scrape_coin_data(self, coin_input: str, timeframe: str, include_trending: bool = False) -> Optional[Dict]:
        """
        Main method to scrape all coin data using pycoingecko.
        
        Args:
            coin_input: Coin name or symbol
            timeframe: 'daily', 'weekly', 'monthly', 'quarterly', or 'yearly'
            include_trending: Whether to include trending coins data
            
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
        # historical_data = self.get_historical_data(coin_id, timeframe)
        historical_data=[]
        # Add small delay to respect rate limits
        time.sleep(0.5)
        
        # Get global market data
        global_data = self.get_global_market_data()
        
        # Get trending coins if requested
        trending_coins = []
        if include_trending:
            time.sleep(0.5)
            trending_coins = self.get_trending_coins()
        
        # Combine all data
        result = {
            **current_data,
            'timeframe': timeframe,
            'historical_prices': historical_data,
            'data_points': len(historical_data),
            'global_market_data': global_data,
            'trending_coins': trending_coins,
            'scraped_at': datetime.now().isoformat(),
            'data_source': 'CoinGecko API (pycoingecko)'
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
            'Fully Diluted Valuation': data['fully_diluted_valuation'],
            '24h Change (%)': data['price_change_24h'],
            '7d Change (%)': data['price_change_7d'],
            '30d Change (%)': data['price_change_30d'],
            '1y Change (%)': data['price_change_1y'],
            'All Time High (USD)': data['ath'],
            'ATH Date': data['ath_date'],
            'All Time Low (USD)': data['atl'],
            'ATL Date': data['atl_date'],
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
                'Ethereum Dominance (%)': global_data.get('ethereum_percentage', 0),
                'Active Cryptocurrencies': global_data.get('active_cryptocurrencies', 0),
                'Total Markets': global_data.get('markets', 0),
                'Market Cap Change 24h (%)': global_data.get('market_cap_change_percentage_24h', 0)
            })
        
        main_df = pd.DataFrame([main_data])
        
        # Create historical data DataFrame
        if data['historical_prices']:
            historical_df = pd.DataFrame(data['historical_prices'])
        else:
            historical_df = pd.DataFrame()
        
        # Create trending coins DataFrame
        trending_df = pd.DataFrame()
        if data.get('trending_coins'):
            trending_df = pd.DataFrame(data['trending_coins'])
        
        # Save to Excel with multiple sheets
        excel_filename = filename.replace('.csv', '.xlsx')
        with pd.ExcelWriter(excel_filename, engine='openpyxl') as writer:
            main_df.to_excel(writer, sheet_name='Current Data', index=False)
            if not historical_df.empty:
                historical_df.to_excel(writer, sheet_name='Historical Prices', index=False)
            if not trending_df.empty:
                trending_df.to_excel(writer, sheet_name='Trending Coins', index=False)
        
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
    print(f"   Fully Diluted Val:    ${data['fully_diluted_valuation']:,}")
    
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
    print(f"   1y:                   {format_change(data['price_change_1y'])}")
    
    # All-Time Records
    print(f"\n🏆 ALL-TIME RECORDS:")
    print(f"   All-Time High:        ${data['ath']:,.8f} ({data['ath_date'][:10] if data['ath_date'] else 'N/A'})")
    print(f"   All-Time Low:         ${data['atl']:,.8f} ({data['atl_date'][:10] if data['atl_date'] else 'N/A'})")
    
    # Global Market Data
    if data.get('global_market_data'):
        global_data = data['global_market_data']
        print(f"\n🌍 GLOBAL MARKET DATA:")
        print(f"   Total Crypto Market Cap: ${global_data.get('total_market_cap_usd', 0):,}")
        print(f"   Total 24h Volume:     ${global_data.get('total_volume_24h_usd', 0):,}")
        print(f"   Bitcoin Dominance:    {global_data.get('bitcoin_percentage', 0):.2f}%")
        print(f"   Ethereum Dominance:   {global_data.get('ethereum_percentage', 0):.2f}%")
        print(f"   Active Cryptocurrencies: {global_data.get('active_cryptocurrencies', 0):,}")
        print(f"   Market Cap Change 24h: {format_change(global_data.get('market_cap_change_percentage_24h', 0))}")
    
    # Trending Coins
    if data.get('trending_coins'):
        print(f"\n🔥 TRENDING COINS:")
        for i, coin in enumerate(data['trending_coins'][:5], 1):
            print(f"   {i}. {coin['name']} ({coin['symbol'].upper()}) - Rank #{coin['market_cap_rank']}")
    
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


def main():
    """Main function to run the scraper."""
    parser = argparse.ArgumentParser(
        description='CoinGecko API Cryptocurrency Data Scraper using pycoingecko',
        epilog='''
Examples:
  python coingecko_scraper.py --coin bitcoin --timeframe weekly
  python coingecko_scraper.py --coin eth --timeframe daily --save-csv
  python coingecko_scraper.py --coin solana --timeframe monthly --json-output
  python coingecko_scraper.py --coin bitcoin --timeframe yearly --trending
        ''',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--coin', '-c', required=True, 
                       help='Coin name or symbol (e.g., bitcoin, btc, ethereum, eth, solana, sol)')
    parser.add_argument('--timeframe', '-t', 
                       choices=['daily', 'weekly', 'monthly', 'quarterly', 'yearly'], 
                       default='weekly', 
                       help='Timeframe for historical data (default: weekly)')
    parser.add_argument('--save-csv', action='store_true', 
                       help='Save results to CSV/Excel files')
    parser.add_argument('--json-output', action='store_true', 
                       help='Output raw JSON data instead of formatted display')
    parser.add_argument('--output-file', '-o', 
                       help='Custom output filename (without extension)')
    parser.add_argument('--trending', action='store_true',
                       help='Include trending coins data')
    parser.add_argument('--api-key', 
                       help='CoinGecko API key for higher rate limits')
    
    args = parser.parse_args()
    
    # Initialize scraper with optional API key
    api_key = args.api_key or os.getenv("COINGECKO_API_KEY")
    scraper = CoinGeckoAPIScraper(api_key=api_key)
    
    try:
        # Initialize LLM service
        llm_service = None
        if os.getenv("GROQ_API_KEY"):
            try:
                llm_service = LLMService(model="openai/gpt-oss-20b")
            except Exception as e:
                print(f"⚠️  Failed to initialize LLM service: {e}")
        
        # Scrape data
        data = scraper.scrape_coin_data(args.coin, args.timeframe, args.trending)
        
        if not data:
            print("❌ Failed to scrape coin data")
            sys.exit(1)
        
        # Output data
        if args.json_output:
            print(json.dumps(data, indent=2, default=str))
        else:
            final_data = print_formatted_output(data)
            
            # Run LLM analysis if available
            if llm_service:
                print("\n🤖 Running LLM analysis...")
                llm_service.analyze_coin(str(final_data))
           
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
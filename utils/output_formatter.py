from typing import Dict
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
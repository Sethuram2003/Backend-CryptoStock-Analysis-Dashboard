from pycoingecko import CoinGeckoAPI
import json
from datetime import datetime

def fetch_crypto_data():
    """
    Fetch cryptocurrency data using CoinGecko and save to JSON
    """
    try:
        # Initialize the CoinGecko API
        cg = CoinGeckoAPI()
        
        # Define the cryptocurrencies you want to track (using CoinGecko IDs)
        crypto_ids = ['bitcoin', 'ethereum', 'cardano', 'solana', 'dogecoin']
        
        all_crypto_data = {}
        
        print("Fetching cryptocurrency data from CoinGecko...")
        
        # Get current price data for all specified cryptocurrencies
        price_data = cg.get_price(
            ids=','.join(crypto_ids), 
            vs_currencies='usd,eur',
            include_market_cap='true',
            include_24hr_vol='true',
            include_24hr_change='true',
            include_last_updated_at='true'
        )
        
        # Get additional market data for each cryptocurrency
        for crypto_id in crypto_ids:
            if crypto_id in price_data:
                print(f"Processing data for {crypto_id}...")
                
                # Get more detailed information
                coin_data = cg.get_coin_by_id(crypto_id)
                
                crypto_info = {
                    "id": crypto_id,
                    "name": coin_data.get('name', 'N/A'),
                    "symbol": coin_data.get('symbol', '').upper(),
                    "current_price_usd": price_data[crypto_id].get('usd', 'N/A'),
                    "current_price_eur": price_data[crypto_id].get('eur', 'N/A'),
                    "market_cap_usd": price_data[crypto_id].get('usd_market_cap', 'N/A'),
                    "market_cap_eur": price_data[crypto_id].get('eur_market_cap', 'N/A'),
                    "24h_volume_usd": price_data[crypto_id].get('usd_24h_vol', 'N/A'),
                    "24h_volume_eur": price_data[crypto_id].get('eur_24h_vol', 'N/A'),
                    "24h_change_percentage": price_data[crypto_id].get('usd_24h_change', 'N/A'),
                    "market_cap_rank": coin_data.get('market_cap_rank', 'N/A'),
                    "circulating_supply": coin_data.get('market_data', {}).get('circulating_supply', 'N/A'),
                    "total_supply": coin_data.get('market_data', {}).get('total_supply', 'N/A'),
                    "max_supply": coin_data.get('market_data', {}).get('max_supply', 'N/A'),
                    "timestamp": datetime.now().isoformat(),
                    "last_updated": price_data[crypto_id].get('last_updated_at', 'N/A')
                }
                
                all_crypto_data[crypto_id] = crypto_info
        
        # Define the filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"crypto_data_{timestamp}.json"
        
        # Save all crypto data to a JSON file
        with open(filename, 'w', encoding='utf-8') as json_file:
            json.dump(all_crypto_data, json_file, indent=2, ensure_ascii=False)
        
        print(f"Crypto data successfully saved to {filename}")
        print(f"Fetched data for {len(crypto_ids)} cryptocurrencies")
        
        return filename
        
    except Exception as err:
        print(f"An error occurred while fetching crypto data: {err}")
        return None

def fetch_crypto_history(coin_id='bitcoin', days=30):
    """
    Fetch historical market data for a specific cryptocurrency
    """
    try:
        cg = CoinGeckoAPI()
        
        print(f"Fetching {days} days of historical data for {coin_id}...")
        
        # Get historical market data
        history_data = cg.get_coin_market_chart_by_id(
            id=coin_id, 
            vs_currency='usd', 
            days=days
        )
        
        historical_data = {
            "coin_id": coin_id,
            "days": days,
            "timestamp": datetime.now().isoformat(),
            "prices": history_data.get('prices', []),
            "market_caps": history_data.get('market_caps', []),
            "total_volumes": history_data.get('total_volumes', [])
        }
        
        filename = f"crypto_history_{coin_id}_{days}days_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, 'w', encoding='utf-8') as json_file:
            json.dump(historical_data, json_file, indent=2)
        
        print(f"Historical crypto data saved to {filename}")
        return filename
        
    except Exception as err:
        print(f"Error fetching historical data for {coin_id}: {err}")
        return None

if __name__ == "__main__":
    # Fetch current crypto data
    fetch_crypto_data()
    
    # Or fetch historical data for Bitcoin (last 30 days)
    # fetch_crypto_history('bitcoin', 30)
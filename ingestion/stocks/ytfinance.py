import yfinance as yf
import json
import pandas as pd
from datetime import datetime

def fetch_stock_data():
    """
    Fetch stock data using yfinance and save to JSON
    """
    try:
        # Define the stock tickers you want to track
        tickers = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN']
        
        all_stock_data = {}
        
        for ticker in tickers:
            print(f"Fetching data for {ticker}...")
            
            # Create a Ticker object
            stock = yf.Ticker(ticker)
            
            # Get current stock info
            info = stock.info
            
            # Get historical data for the last day
            hist = stock.history(period="1d", interval="1m")
            
            # Prepare the data for JSON serialization
            stock_data = {
                "ticker": ticker,
                "company_name": info.get('longName', 'N/A'),
                "current_price": info.get('currentPrice', 'N/A'),
                "previous_close": info.get('previousClose', 'N/A'),
                "market_cap": info.get('marketCap', 'N/A'),
                "volume": info.get('volume', 'N/A'),
                "timestamp": datetime.now().isoformat(),
                "historical_data": []
            }
            
            # Add historical minute-by-minute data if available
            if not hist.empty:
                for index, row in hist.iterrows():
                    stock_data["historical_data"].append({
                        "datetime": index.isoformat(),
                        "open": float(row['Open']),
                        "high": float(row['High']),
                        "low": float(row['Low']),
                        "close": float(row['Close']),
                        "volume": int(row['Volume'])
                    })
            
            all_stock_data[ticker] = stock_data
        
        # Define the filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"stock_data_{timestamp}.json"
        
        # Save all stock data to a JSON file
        with open(filename, 'w', encoding='utf-8') as json_file:
            json.dump(all_stock_data, json_file, indent=2, ensure_ascii=False)
        
        print(f"Stock data successfully saved to {filename}")
        print(f"Fetched data for {len(tickers)} stocks")
        
        return filename
        
    except Exception as err:
        print(f"An error occurred while fetching stock data: {err}")
        return None

def fetch_single_stock(ticker):
    """
    Fetch data for a single stock
    """
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        stock_data = {
            "ticker": ticker,
            "company_name": info.get('longName', 'N/A'),
            "current_price": info.get('currentPrice', 'N/A'),
            "day_high": info.get('dayHigh', 'N/A'),
            "day_low": info.get('dayLow', 'N/A'),
            "volume": info.get('volume', 'N/A'),
            "market_cap": info.get('marketCap', 'N/A'),
            "timestamp": datetime.now().isoformat()
        }
        
        filename = f"stock_{ticker}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, 'w', encoding='utf-8') as json_file:
            json.dump(stock_data, json_file, indent=2, ensure_ascii=False)
        
        print(f"Single stock data saved to {filename}")
        return filename
        
    except Exception as err:
        print(f"Error fetching data for {ticker}: {err}")
        return None

if __name__ == "__main__":
    # Fetch data for multiple stocks
    fetch_stock_data()
    
    # Or fetch data for a single stock
    # fetch_single_stock("AAPL")
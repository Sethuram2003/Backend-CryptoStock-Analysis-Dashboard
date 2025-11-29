import yfinance as yf
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any


def _now_iso_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


DEFAULT_TICKERS = ["AAPL", "MSFT", "AMZN", "GOOGL", "TSLA"]


def fetch_stock_history(
    ticker: str = "AAPL",
    days: int = 30,
) -> Dict[str, Any]:

    stock = yf.Ticker(ticker)
    df = stock.history(period=f"{days}d")

    # Transform into CoinGecko-like structure
    prices = [
        [int(row[0].timestamp() * 1000), row[1]["Close"]]
        for row in df.iterrows()
    ]

    payload = {
        "ticker": ticker,
        "days": days,
        "timestamp": _now_iso_utc(),
        "prices": prices,
        "raw_history": df.to_dict(),  # optional, can remove if heavy
    }

    return {"fetched_at": _now_iso_utc(), "data": payload}



def fetch_stock_data(
    tickers: Optional[List[str]] = None,
) -> Dict[str, Any]:

    tickers = tickers or DEFAULT_TICKERS
    all_stock_data = {}

    for symbol in tickers:

        stock = yf.Ticker(symbol)
        info = stock.fast_info  # faster, recent versions of yfinance

        stock_info = {
            "symbol": symbol,
            "current_price": info.get("last_price", "N/A"),
            "previous_close": info.get("previous_close", "N/A"),
            "open_price": info.get("open", "N/A"),
            "day_high": info.get("day_high", "N/A"),
            "day_low": info.get("day_low", "N/A"),
            "market_cap": info.get("market_cap", "N/A"),
            "volume": info.get("volume", "N/A"),
            "exchange": info.get("exchange", "N/A"),
            "currency": info.get("currency", "USD"),
            "timestamp": _now_iso_utc(),
        }

        all_stock_data[symbol] = stock_info

    return {"fetched_at": _now_iso_utc(), "data": all_stock_data}


if __name__ == "__main__":
    data = fetch_stock_data()
    historical = fetch_stock_history(ticker="AAPL", days=7)

    print(historical)
    print("-----")
    print(data)

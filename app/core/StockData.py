import logging
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any

import pandas as pd
import yfinance as yf

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _now_iso_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


DEFAULT_TICKERS = ["AAPL", "MSFT", "AMZN", "GOOGL", "TSLA"]


def fetch_stock_history(ticker: str = "AAPL", days: int = 30) -> Dict[str, Any]:
    stock = yf.Ticker(ticker)
    try:
        df = stock.history(period=f"{days}d")
    except Exception as e:
        logger.exception("Failed to fetch history for %s", ticker)
        return {
            "fetched_at": _now_iso_utc(),
            "error": f"history fetch failed for {ticker}: {e}",
            "data": None,
        }

    if df is None or df.empty:
        return {
            "fetched_at": _now_iso_utc(),
            "error": f"no history available for {ticker}",
            "data": {"ticker": ticker, "days": days, "prices": []},
        }

    prices = []
    for idx, row in df.iterrows():
        try:
            ts_ms = int(pd.Timestamp(idx).timestamp() * 1000)
            close = float(row["Close"])
            prices.append([ts_ms, close])
        except Exception:
            continue

    payload = {
        "ticker": ticker,
        "days": days,
        "timestamp": _now_iso_utc(),
        "prices": prices,
    }

    return {"fetched_at": _now_iso_utc(), "data": payload}


def _get_last_price_from_history(stock: yf.Ticker) -> Optional[float]:
    try:
        h = stock.history(period="5d")
        if h is not None and not h.empty:
            return float(h["Close"].dropna().iloc[-1])
    except Exception:
        return None
    return None


def fetch_stock_data(tickers: Optional[List[str]] = None) -> Dict[str, Any]:
    tickers = tickers or DEFAULT_TICKERS
    all_stock_data: Dict[str, Any] = {}
    errors: Dict[str, str] = {}

    for symbol in tickers:
        try:
            stock = yf.Ticker(symbol)

            try:
                info = getattr(stock, "fast_info", {}) or {}
            except Exception:
                info = {}

            last_price = info.get("lastPrice")
            prev_close = info.get("previousClose")
            open_price = info.get("open")
            day_high = info.get("dayHigh")
            day_low = info.get("dayLow")
            market_cap = info.get("marketCap")
            volume = info.get("lastVolume")
            exchange = info.get("exchange")
            currency = info.get("currency")

            if last_price in (None, "N/A"):
                last_price = _get_last_price_from_history(stock)
                if last_price is None:
                    try:
                        slow_info = stock.info or {}
                        last_price = slow_info.get("regularMarketPrice", "N/A")
                        prev_close = prev_close or slow_info.get("previousClose")
                        market_cap = market_cap or slow_info.get("marketCap")
                        currency = currency or slow_info.get("currency")
                        exchange = exchange or slow_info.get("exchange")
                    except Exception:
                        last_price = last_price if last_price is not None else "N/A"

            stock_info = {
                "symbol": symbol,
                "current_price": last_price if last_price is not None else "N/A",
                "previous_close": prev_close if prev_close is not None else "N/A",
                "open_price": open_price if open_price is not None else "N/A",
                "day_high": day_high if day_high is not None else "N/A",
                "day_low": day_low if day_low is not None else "N/A",
                "market_cap": market_cap if market_cap is not None else "N/A",
                "volume": volume if volume is not None else "N/A",
                "exchange": exchange if exchange is not None else "N/A",
                "currency": currency if currency is not None else "USD",
                "timestamp": _now_iso_utc(),
            }

            all_stock_data[symbol] = stock_info

        except Exception as e:
            logger.exception("Error fetching data for %s", symbol)
            errors[symbol] = str(e)
            all_stock_data[symbol] = {
                "symbol": symbol,
                "error": str(e),
                "timestamp": _now_iso_utc(),
            }

    return {"fetched_at": _now_iso_utc(), "data": all_stock_data, "errors": errors}


if __name__ == "__main__":
    data = fetch_stock_data(["MSFT"])
    historical = fetch_stock_history(ticker="MSFT", days=7)
    print("-----")
    print(data)

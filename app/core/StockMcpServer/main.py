from typing import Any, Optional
import json
import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Stock Data and sentiment analysis Tools")

BASE_URL = "https://crypto-and-stock-analysis-da-and-ag.vercel.app"


async def make_request(endpoint: str, method: str = "GET") -> Any:
    """Generic request wrapper for both Crypto and Stock API."""
    url = f"{BASE_URL}{endpoint}"

    async with httpx.AsyncClient() as client:
        try:
            if method == "GET":
                response = await client.get(url, timeout=30.0)
            elif method == "PUT":
                response = await client.put(url, timeout=30.0)
            else:
                raise ValueError("Unsupported HTTP method")

            response.raise_for_status()
            return response.json()

        except httpx.HTTPStatusError as e:
            print(f"HTTP error ({e.response.status_code}): {e}")
            return None
        except httpx.RequestError as e:
            print(f"Request error: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error: {e}")
            return None


@mcp.tool(
    description="Fetch real-time stock market data (price, open, high, low, market cap, volume, exchange). "
)
async def get_stock_data(ticker: str = "AAPL") -> str:
    data = await make_request(f"/get-stock-data?ticker={ticker}")

    if not data:
        return f"Error: Failed to fetch stock data for {ticker}"
    return json.dumps(data)


@mcp.tool(
    description="Fetch stock sentiment for the past N days (top financial news, article sentiment, "
)
async def put_stock_sentiment(ticker: str = "AAPL", days: int = 7) -> str:
    data = await make_request(
        f"/put-stock-sentiment?ticker={ticker}&days={days}",
        method="PUT"
    )

    if not data:
        return f"Error: Failed to fetch sentiment for {ticker}"
    return json.dumps(data)



if __name__ == "__main__":
    mcp.run(transport='stdio')

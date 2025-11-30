from typing import Any
import json
import httpx
from bs4 import BeautifulSoup
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Crypto Data and Sentiment Tools")

BASE_URL = "https://crypto-and-stock-analysis-da-and-ag.vercel.app"


async def make_crypto_request(endpoint: str, method: str = "GET") -> Any:
    """Generic request wrapper for Crypto API"""
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
    description="Fetch real-time crypto market data for a given coin, including price, market cap, and other key metrics."
)
async def get_crypto_data(coin_id: str = "bitcoin") -> str:
    """
    Calls the /get-crypto-data endpoint.
    Example:
      get_crypto_data("bitcoin")
    """
    data = await make_crypto_request(f"/get-crypto-data?coin_id={coin_id}")
    if not data:
        return "Error: Failed to fetch crypto data"
    return json.dumps(data)


@mcp.tool(
    description=(
        "Get crypto sentiment analysis for a coin over a specified number of days. "
        "Returns the top 3 news links with individual sentiment scores, the overall sentiment, "
        "and a trend indicating whether the sentiment is increasing or decreasing."
    )
)
async def put_crypto_sentiment(coin_id: str = "bitcoin", days: int = 7) -> str:
    """
    Calls the /put-crypto-sentiment endpoint (PUT).
    Example:
      put_crypto_sentiment("bitcoin", 7)
    """
    data = await make_crypto_request(
        f"/put-crypto-sentiment?coin_id={coin_id}&days={days}", 
        method="PUT"
    )
    if not data:
        return "Error: Failed to fetch crypto sentiment"
    return json.dumps(data)

@mcp.tool(
    description="Fetch visible text contents of a URL (HTML removed)"
)
async def get_data_url(url: str, limit: int = 5000) -> str:
    """
    Takes in the URL of a website and returns readable text content only,
    stripping out HTML, scripts, and styles.
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            # Remove script and style elements
            for tag in soup(["script", "style", "noscript"]):
                tag.extract()

            text = soup.get_text(separator="\n").strip()

            # Clean excessive whitespace
            cleaned = "\n".join(
                line.strip() for line in text.splitlines() if line.strip()
            )

            # Apply character limit
            if len(cleaned) > limit:
                return cleaned[:limit] + "\n\n...[TRUNCATED]..."

            return cleaned

    except httpx.RequestError as e:
        return f"Request error occurred: {str(e)}"
    except httpx.HTTPStatusError as e:
        return f"HTTP error occurred: {str(e)}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"



if __name__ == "__main__":
    mcp.run(transport='stdio')

from pycoingecko import CoinGeckoAPI
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any

def _now_iso_utc() -> str:
    return datetime.now(timezone.utc).isoformat()

DEFAULT_IDS = ['bitcoin', 'ethereum', 'cardano', 'solana', 'dogecoin']

def fetch_crypto_history(
    coin_id: str = "bitcoin",
    days: int = 30,
) -> Dict[str, Any]:


    cg = CoinGeckoAPI()
    history = cg.get_coin_market_chart_by_id(id=coin_id, vs_currency="usd", days=days)

    payload = {
        "coin_id": coin_id,
        "days": days,
        "timestamp": _now_iso_utc(),
        "prices": history.get("prices", []),
        "market_caps": history.get("market_caps", []),
        "total_volumes": history.get("total_volumes", [])
    }

    return {"fetched_at": _now_iso_utc(), "data": payload}

def fetch_crypto_data(
    crypto_ids: Optional[List[str]] = None,
) -> Dict[str, Any]:
    crypto_ids = crypto_ids or DEFAULT_IDS
    

    cg = CoinGeckoAPI()
    all_crypto_data = {}

    price_data = cg.get_price(
        ids=",".join(crypto_ids),
        vs_currencies="usd,eur",
        include_market_cap=True,
        include_24hr_vol=True,
        include_24hr_change=True,
        include_last_updated_at=True
    )

    for cid in crypto_ids:
        if cid not in price_data:
            continue
        coin = cg.get_coin_by_id(cid)
        pd = price_data[cid]

        crypto_info = {
            "id": cid,
            "name": coin.get("name", "N/A"),
            "symbol": coin.get("symbol", "").upper(),
            "current_price_usd": pd.get("usd", "N/A"),
            "current_price_eur": pd.get("eur", "N/A"),
            "market_cap_usd": pd.get("usd_market_cap", "N/A"),
            "market_cap_eur": pd.get("eur_market_cap", "N/A"),
            "24h_volume_usd": pd.get("usd_24h_vol", "N/A"),
            "24h_volume_eur": pd.get("eur_24h_vol", "N/A"),
            "24h_change_percentage": pd.get("usd_24h_change", "N/A"),
            "market_cap_rank": coin.get("market_cap_rank", "N/A"),
            "circulating_supply": coin.get("market_data", {}).get("circulating_supply", "N/A"),
            "total_supply": coin.get("market_data", {}).get("total_supply", "N/A"),
            "max_supply": coin.get("market_data", {}).get("max_supply", "N/A"),
            "timestamp": _now_iso_utc(),
            "last_updated_epoch": pd.get("last_updated_at", "N/A")
        }
        all_crypto_data[cid] = crypto_info

 

    return {"fetched_at": _now_iso_utc(), "data": all_crypto_data}

if __name__ == "__main__":
    data = fetch_crypto_data()
    historical_data = fetch_crypto_history(coin_id="bitcoin", days=7)
    print(historical_data)
    print("-----")
    print(data)
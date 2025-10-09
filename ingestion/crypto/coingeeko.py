# ingestion/crypto/coingeeko.py
from pycoingecko import CoinGeckoAPI
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional, Dict, Any

# --- FastAPI router bits
from fastapi import APIRouter, Query
from pydantic import BaseModel

DEFAULT_IDS = ['bitcoin', 'ethereum', 'cardano', 'solana', 'dogecoin']
DATA_DIR = Path("ingestion/data/crypto")

def _now_iso_utc() -> str:
    return datetime.now(timezone.utc).isoformat()

def fetch_crypto_data(
    crypto_ids: Optional[List[str]] = None,
    output_dir: Optional[str] = None
) -> Dict[str, Any]:
    crypto_ids = crypto_ids or DEFAULT_IDS
    outdir = Path(output_dir or DATA_DIR)
    outdir.mkdir(parents=True, exist_ok=True)

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

    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    path = outdir / f"crypto_data_{ts}.json"
    with path.open("w", encoding="utf-8") as f:
        json.dump(all_crypto_data, f, indent=2, ensure_ascii=False)

    return {"path": str(path), "count": len(all_crypto_data)}

def fetch_crypto_history(
    coin_id: str = "bitcoin",
    days: int = 30,
    output_dir: Optional[str] = None
) -> Dict[str, Any]:
    outdir = Path(output_dir or DATA_DIR)
    outdir.mkdir(parents=True, exist_ok=True)

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

    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    path = outdir / f"crypto_history_{coin_id}_{days}days_{ts}.json"
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

    return {"path": str(path), "coin_id": coin_id}

# ---------- FastAPI Router ----------
class IngestResult(BaseModel):
    path: str
    count: Optional[int] = None
    coin_id: Optional[str] = None

router = APIRouter(prefix="/ingest/crypto", tags=["crypto"])

@router.post("", response_model=IngestResult)
def ingest_crypto(ids: Optional[str] = Query(None, description="Comma-separated CoinGecko IDs"),
                  output_dir: Optional[str] = None):
    crypto_ids: Optional[List[str]] = None
    if ids:
        crypto_ids = [s.strip() for s in ids.split(",") if s.strip()]
    return fetch_crypto_data(crypto_ids=crypto_ids, output_dir=output_dir or str(DATA_DIR))

@router.post("/history", response_model=IngestResult)
def ingest_crypto_history(coin_id: str = "bitcoin",
                          days: int = 30,
                          output_dir: Optional[str] = None):
    return fetch_crypto_history(coin_id=coin_id, days=days, output_dir=output_dir or str(DATA_DIR))

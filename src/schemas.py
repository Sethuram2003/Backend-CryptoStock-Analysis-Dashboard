from pydantic import BaseModel
from typing import Optional

class BothResult(BaseModel):
    crypto: dict
    stocks: dict

class IngestResult(BaseModel):
    count: Optional[int] = None
    coin_id: Optional[str] = None
from pydantic import BaseModel
from typing import Optional

class BothResult(BaseModel):
    crypto: dict
    stocks: dict


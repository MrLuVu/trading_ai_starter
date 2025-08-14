from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
from ..strategy.strategy import Strategy, StrategyConfig
from ..utils.logger import get_logger

logger = get_logger("signal_service")
app = FastAPI()
strategy = Strategy(StrategyConfig())

class Bar(BaseModel):
    time: str
    Open: float
    High: float
    Low: float
    Close: float

class BarsPayload(BaseModel):
    bars: list[Bar]

@app.post("/signal")
def signal(payload: BarsPayload):
    df = pd.DataFrame([b.model_dump() for b in payload.bars])
    df["time"] = pd.to_datetime(df["time"])
    sig = strategy.on_bar(df)
    logger.info(f"Signal: {sig}")
    return sig

import os
from dotenv import load_dotenv

load_dotenv()

def env_str(key, default=None):
    return os.getenv(key, default)

def env_float(key, default=0.0):
    try:
        return float(os.getenv(key, default))
    except Exception:
        return default

def env_int(key, default=0):
    try:
        return int(os.getenv(key, default))
    except Exception:
        return default

SYMBOL = env_str("SYMBOL", "EURUSD")
TIMEFRAME = env_str("TIMEFRAME", "M5")
LOT_SIZE = env_float("LOT_SIZE", 0.10)
MAX_SPREAD_PIPS = env_float("MAX_SPREAD_PIPS", 1.2)

STOP_LOSS_PIPS = env_float("STOP_LOSS_PIPS", 10.0)
TAKE_PROFIT_PIPS = env_float("TAKE_PROFIT_PIPS", 20.0)
DAILY_MAX_DD_PCT = env_float("DAILY_MAX_DD_PCT", 5.0)

POLL_SECONDS = env_int("POLL_SECONDS", 5)
DEVIATION = env_int("DEVIATION", 10)
MAGIC = env_int("MAGIC", 777001)
COMMENT = env_str("COMMENT", "TradingAI")

STRATEGY_NAME = env_str("STRATEGY_NAME", "sma")
SMA_FAST = env_int("SMA_FAST", 20)
SMA_SLOW = env_int("SMA_SLOW", 50)

DATA_DIR = env_str("DATA_DIR", "data")
LOG_LEVEL = env_str("LOG_LEVEL", "INFO")

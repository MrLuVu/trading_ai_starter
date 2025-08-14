import numpy as np
import pandas as pd
import talib

def rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    up = delta.clip(lower=0).ewm(alpha=1/period, adjust=False).mean()
    down = -delta.clip(upper=0).ewm(alpha=1/period, adjust=False).mean()
    rs = up / (down.replace(0, np.nan))
    return 100 - (100 / (1 + rs))

def atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    high, low, close = df["High"], df["Low"], df["Close"]
    prev_close = close.shift(1)
    tr = np.maximum(high - low, np.maximum(abs(high - prev_close), abs(low - prev_close)))
    return tr.ewm(alpha=1/period, adjust=False).mean()

def add_basic_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["ret1"] = out["Close"].pct_change(1)
    out["ret5"] = out["Close"].pct_change(5)
    out["rsi14"] = rsi(out["Close"], 14)
    out["atr14"] = atr(out[["High","Low","Close"]], 14)
    out["%b"] = (out["Close"] - out["Close"].rolling(20).mean()) / (2*out["Close"].rolling(20).std(ddof=0))
    out["tod"] = out["time"].dt.hour if "time" in out.columns and np.issubdtype(out["time"].dtype, np.datetime64) else 0
    return out

def create_features(df):
    df['SMA_10'] = talib.SMA(df['close'], timeperiod=10)
    df['SMA_30'] = talib.SMA(df['close'], timeperiod=30)
    df['RSI_14'] = talib.RSI(df['close'], timeperiod=14)
    df['ATR_14'] = talib.ATR(df['high'], df['low'], df['close'], timeperiod=14)
    df['Momentum_10'] = talib.MOM(df['close'], timeperiod=10)
    
    df = df.dropna()
    return df

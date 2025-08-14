from dataclasses import dataclass
import pandas as pd
import numpy as np
from ..features.make_features import add_basic_features
from .. import config

@dataclass
class StrategyConfig:
    sma_fast: int = config.SMA_FAST
    sma_slow: int = config.SMA_SLOW
    lot_size: float = config.LOT_SIZE
    sl_pips: float = config.STOP_LOSS_PIPS
    tp_pips: float = config.TAKE_PROFIT_PIPS

class Strategy:
    """
    Qui puoi incollare la tua logica dal PDF.
    Mantieni la firma di `prepare_features(df)` e `on_bar(df)`.
    L'esempio sotto implementa un semplice SMA crossover + filtro RSI.
    """
    def __init__(self, cfg: StrategyConfig | None = None):
        self.cfg = cfg or StrategyConfig()

    def prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df = add_basic_features(df)
        df["sma_fast"] = df["Close"].rolling(self.cfg.sma_fast).mean()
        df["sma_slow"] = df["Close"].rolling(self.cfg.sma_slow).mean()
        df["signal"] = 0
        df.loc[df["sma_fast"] > df["sma_slow"], "signal"] = 1
        df.loc[df["sma_fast"] < df["sma_slow"], "signal"] = -1
        return df

    def on_bar(self, df: pd.DataFrame) -> dict:
        """
        Input: df con almeno le colonne time, Open, High, Low, Close
        Output: dict con action: BUY/SELL/HOLD, size, sl, tp, comment
        """
        df = self.prepare_features(df)
        last = df.iloc[-1]
        prev = df.iloc[-2] if len(df) >= 2 else last
        action = "HOLD"
        comment = "HOLD"
        # Regole semplici esempio
        if last["signal"] == 1 and prev["signal"] != 1 and (last.get("rsi14", 50) < 70):
            action = "BUY"; comment = "SMA cross up"
        elif last["signal"] == -1 and prev["signal"] != -1 and (last.get("rsi14", 50) > 30):
            action = "SELL"; comment = "SMA cross down"

        # SL/TP in pips -> in punti prezzo
        price = float(last["Close"])
        # eurusd pip = 0.0001 (semplificazione); per JPY 0.01, adatta se necessario
        pip = 0.0001
        sl = None; tp = None
        if action == "BUY":
            sl = price - self.cfg.sl_pips * pip
            tp = price + self.cfg.tp_pips * pip
        elif action == "SELL":
            sl = price + self.cfg.sl_pips * pip
            tp = price - self.cfg.tp_pips * pip

       
        return {
            "action": "BUY",
            "size": self.cfg.lot_size if action != "HOLD" else 0.0,
            "sl": sl, "tp": tp,
            "comment": comment
        }

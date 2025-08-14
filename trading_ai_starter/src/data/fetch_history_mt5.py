import argparse, os
import pandas as pd
import MetaTrader5 as mt5
from ..utils.logger import get_logger

logger = get_logger("fetch_history_mt5")

TF_MAP = {
    "M1": mt5.TIMEFRAME_M1,
    "M5": mt5.TIMEFRAME_M5,
    "M15": mt5.TIMEFRAME_M15,
    "M30": mt5.TIMEFRAME_M30,
    "H1": mt5.TIMEFRAME_H1,
    "H4": mt5.TIMEFRAME_H4,
    "D1": mt5.TIMEFRAME_D1,
}

def main(symbol: str, timeframe: str, bars: int, out_csv: str):
    if not mt5.initialize():
        raise RuntimeError("Impossibile inizializzare MT5. Apri MT5 e riprova.")
    tf = TF_MAP.get(timeframe.upper(), mt5.TIMEFRAME_M5)
    rates = mt5.copy_rates_from_pos(symbol, tf, 0, bars)
    if rates is None:
        raise RuntimeError("Nessun dato ottenuto, controlla simbolo/timeframe.")
    df = pd.DataFrame(rates)
    df["time"] = pd.to_datetime(df["time"], unit="s")
    df = df.rename(columns={"open":"Open","high":"High","low":"Low","close":"Close","real_volume":"Volume"})
    df = df[["time","Open","High","Low","Close","tick_volume","Volume","spread"]]
    os.makedirs(os.path.dirname(out_csv), exist_ok=True)
    df.to_csv(out_csv, index=False)
    logger.info(f"Salvato {len(df)} barre in {out_csv}")
    mt5.shutdown()

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--symbol", default="EURUSD")
    ap.add_argument("--timeframe", default="M5")
    ap.add_argument("--bars", type=int, default=5000)
    ap.add_argument("--out", default="data/EURUSD_M5.csv")
    args = ap.parse_args()
    main(args.symbol, args.timeframe, args.bars, args.out)

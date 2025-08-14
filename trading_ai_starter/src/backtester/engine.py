import argparse, pandas as pd, numpy as np
from ..strategy.strategy import Strategy, StrategyConfig

def backtest(csv_path: str, lot_size: float = 0.1, sl_pips: float = 10, tp_pips: float = 20, spread_pips: float = 0.2):
    df = pd.read_csv(csv_path)
    df["time"] = pd.to_datetime(df["time"])
    strat = Strategy(StrategyConfig(lot_size=lot_size, sl_pips=sl_pips, tp_pips=tp_pips))
    equity = 10000.0
    balance = equity
    pos = None  # {'side': 'long'/'short', 'entry': price, 'sl': price, 'tp': price}
    pnl_list = []

    pip = 0.0001  # eurusd
    for i in range(100, len(df)):
        window = df.iloc[:i].copy()
        signal = strat.on_bar(window)
        price = float(window.iloc[-1]["Close"])
        # Execution with simple spread/slippage model
        ask = price + spread_pips * pip / 2
        bid = price - spread_pips * pip / 2

        # manage existing position
        if pos is not None:
            high = float(window.iloc[-1]["High"])
            low  = float(window.iloc[-1]["Low"])
            if pos["side"] == "long":
                if high >= pos["tp"]:
                    pnl = (pos["tp"] - pos["entry"]) / pip * 1.0
                    balance += pnl
                    pnl_list.append(pnl); pos = None
                elif low <= pos["sl"]:
                    pnl = (pos["sl"] - pos["entry"]) / pip * 1.0
                    balance += pnl
                    pnl_list.append(pnl); pos = None
            else:  # short
                if low <= pos["tp"]:
                    pnl = (pos["entry"] - pos["tp"]) / pip * 1.0
                    balance += pnl
                    pnl_list.append(pnl); pos = None
                elif high >= pos["sl"]:
                    pnl = (pos["entry"] - pos["sl"]) / pip * 1.0
                    balance += pnl
                    pnl_list.append(pnl); pos = None

        # enter new position if flat
        if pos is None:
            if signal["action"] == "BUY":
                pos = {"side":"long","entry":ask,"sl":signal["sl"],"tp":signal["tp"]}
            elif signal["action"] == "SELL":
                pos = {"side":"short","entry":bid,"sl":signal["sl"],"tp":signal["tp"]}

    pnl_total = sum(pnl_list)
    trades = len(pnl_list)
    avg = pnl_total / trades if trades else 0
    print(f"Balance finale: {balance:.2f} (pnl totale pips: {pnl_total:.1f})")
    print(f"Trades: {trades}, Avg pips: {avg:.2f}")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True, help="CSV OHLCV con colonne: time, Open, High, Low, Close, ...")
    ap.add_argument("--strategy", default="sma")
    ap.add_argument("--lot", type=float, default=0.1)
    ap.add_argument("--sl", type=float, default=10)
    ap.add_argument("--tp", type=float, default=20)
    ap.add_argument("--spread", type=float, default=0.2)
    args = ap.parse_args()
    backtest(args.csv, lot_size=args.lot, sl_pips=args.sl, tp_pips=args.tp, spread_pips=args.spread)

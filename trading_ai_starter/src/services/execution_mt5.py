import time
import MetaTrader5 as mt5
import pandas as pd
from .. import config
from ..utils.logger import get_logger
from ..strategy.strategy import Strategy, StrategyConfig

logger = get_logger("execution_mt5")

TF_MAP = {
    "M1": mt5.TIMEFRAME_M1,
    "M5": mt5.TIMEFRAME_M5,
    "M15": mt5.TIMEFRAME_M15,
    "M30": mt5.TIMEFRAME_M30,
    "H1": mt5.TIMEFRAME_H1,
    "H4": mt5.TIMEFRAME_H4,
    "D1": mt5.TIMEFRAME_D1,
}

def get_df(symbol: str, timeframe: str, bars: int = 300) -> pd.DataFrame:
    tf = TF_MAP.get(timeframe.upper(), mt5.TIMEFRAME_M5)
    rates = mt5.copy_rates_from_pos(symbol, tf, 0, bars)
    if rates is None or len(rates) == 0:
        return pd.DataFrame()
    df = pd.DataFrame(rates)
    df["time"] = pd.to_datetime(df["time"], unit="s")
    df = df.rename(columns={"open":"Open","high":"High","low":"Low","close":"Close"})
    return df[["time","Open","High","Low","Close"]]

def check_spread_ok(symbol: str, max_spread_pips: float) -> bool:
    tick = mt5.symbol_info_tick(symbol)
    info = mt5.symbol_info(symbol)
    if not tick or not info:
        return False
    spread = (tick.ask - tick.bid)
    pip = 0.0001
    spread_pips = spread / pip
    return spread_pips <= max_spread_pips

def place_order(symbol: str, action: str, volume: float, sl: float|None, tp: float|None):
    tick = mt5.symbol_info_tick(symbol)
    price = tick.ask if action == "BUY" else tick.bid
    order_type = mt5.ORDER_TYPE_BUY if action == "BUY" else mt5.ORDER_TYPE_SELL
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": volume,
        "type": order_type,
        "price": price,
        "sl": sl if sl else 0.0,
        "tp": tp if tp else 0.0,
        "deviation": config.DEVIATION,
        "magic": config.MAGIC,
        "comment": config.COMMENT,
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }
    result = mt5.order_send(request)
    logger.info(f"order_send: {result}")
    return result

def main():
    if not mt5.initialize():
        raise RuntimeError("Impossibile inizializzare MT5 (apri MetaTrader e riprova).")
    symbol = config.SYMBOL
    timeframe = config.TIMEFRAME
    strat = Strategy(StrategyConfig())

    while True:
        try:
            df = get_df(symbol, timeframe, 400)
            if df.empty or len(df) < 100:
                time.sleep(config.POLL_SECONDS); continue
            if not check_spread_ok(symbol, config.MAX_SPREAD_PIPS):
                logger.info("Spread troppo alto, salto.")
                time.sleep(config.POLL_SECONDS); continue
            sig = strat.on_bar(df)
            if sig["action"] in ("BUY","SELL") and sig["size"] > 0:
                place_order(symbol, sig["action"], sig["size"], sig["sl"], sig["tp"])
            else:
                logger.info("HOLD")
            time.sleep(config.POLL_SECONDS)
        except KeyboardInterrupt:
            break
        except Exception as e:
            logger.exception(e)
            time.sleep(config.POLL_SECONDS)

    mt5.shutdown()

if __name__ == "__main__":
    main()

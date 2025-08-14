import logging, sys
from .. import config

def get_logger(name: str):
    logger = logging.getLogger(name)
    if not logger.handlers:
        level = getattr(logging, config.LOG_LEVEL.upper(), logging.INFO)
        logger.setLevel(level)
        h = logging.StreamHandler(sys.stdout)
        h.setLevel(level)
        fmt = logging.Formatter('%(asctime)s | %(levelname)s | %(name)s | %(message)s')
        h.setFormatter(fmt)
        logger.addHandler(h)
    return logger

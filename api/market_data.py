# api/market_data.py
import functools
import yfinance as yf
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

@functools.lru_cache(maxsize=1)
def _load_data(symbols_tuple):
    symbols = list(symbols_tuple)
    start = (datetime.today() - timedelta(days=20)).strftime('%Y-%m-%d')
    end = datetime.today().strftime('%Y-%m-%d')
    df = yf.download(
        symbols,
        start=start,
        end=end,
        progress=False,
        threads=False
    )
    return df["Close"]

def calculate_rsi(series: pd.Series, window=14) -> float:
    delta = series.diff()
    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)
    avg_gain = pd.Series(gain).rolling(window, min_periods=1).mean()
    avg_loss = pd.Series(loss).rolling(window, min_periods=1).mean()
    rs = avg_gain / (avg_loss + 1e-10)
    rsi = 100 - (100 / (1 + rs))
    return float(rsi.iloc[-1])

def handler(request):
    qs = request.args.get("symbols", "")
    symbols = qs.split(",") if qs else ["^NDX", "^SOX", "XLK", "^VIX"]
    raw = _load_data(tuple(symbols))
    if raw.empty:
        return {"error": "データ取得失敗"}

    dates = raw.index[-5:]
    prev_date = dates[-2].strftime('%Y-%m-%d')
    last_date = dates[-1].strftime('%Y-%m-%d')
    result = {}
    for sym in symbols:
        if sym not in raw.columns:
            continue
        prev_close = float(raw.loc[prev_date, sym])
        last_close = float(raw.loc[last_date, sym])
        pct = round((last_close - prev_close) / prev_close * 100, 2)
        rsi = round(calculate_rsi(raw[sym]), 2)
        result[sym] = {
            "prev_date": prev_date,
            "last_date": last_date,
            "prev_close": prev_close,
            "last_close": last_close,
            "pct_change": pct,
            "rsi": rsi
        }
    return result

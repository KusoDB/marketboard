# api/ndx_change.py
import functools
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

@functools.lru_cache(maxsize=1)
def _compute_ndx():
    ticker = "^NDX"
    end = datetime.today()
    start = end - timedelta(days=14)
    df = yf.download(
        ticker,
        start=start.strftime('%Y-%m-%d'),
        end=end.strftime('%Y-%m-%d'),
        progress=False
    )
    df.index = pd.to_datetime(df.index)
    fridays = df[df.index.weekday == 4]
    if len(fridays) < 2:
        return {"error": "データ不足"}
    prev, last = fridays.iloc[-2], fridays.iloc[-1]
    prev_close = float(prev["Close"])
    last_close = float(last["Close"])
    pct = round((last_close - prev_close) / prev_close * 100, 2)
    return {
        "prev_date": fridays.index[-2].strftime('%Y-%m-%d'),
        "last_date": fridays.index[-1].strftime('%Y-%m-%d'),
        "prev_close": prev_close,
        "last_close": last_close,
        "pct_change": pct
    }

def handler(request):
    return _compute_ndx()

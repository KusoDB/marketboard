# api/dev_server.py
from flask import Flask, jsonify, request
import os, requests
import functools
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / ".env") # .env の内容を os.environ に読み込む
print(">> NASDAQ_DATA_LINK_KEY:", os.environ.get("NASDAQ_DATA_LINK_KEY"))

app = Flask(__name__)

# ① 過去20日分のCloseデータをキャッシュ付きで取得
@functools.lru_cache(maxsize=1)
def _load_data(symbols_tuple):
    symbols = list(symbols_tuple)
    start = (datetime.today() - timedelta(days=20)).strftime('%Y-%m-%d')
    end   = datetime.today().strftime('%Y-%m-%d')
    # 'Close' 列だけ返す
    df = yf.download(
        symbols,
        start=start,
        end=end,
        progress=False,
        threads=False
    )["Close"]
    return df

# ② RSI計算（Series→float）
def calculate_rsi(series: pd.Series, window=14) -> float:
    delta = series.diff()
    gain  = np.where(delta >  0, delta, 0)
    loss  = np.where(delta <  0, -delta, 0)
    avg_gain = pd.Series(gain).rolling(window, min_periods=1).mean()
    avg_loss = pd.Series(loss).rolling(window, min_periods=1).mean()
    rs = avg_gain / (avg_loss + 1e-10)
    rsi = 100 - (100 / (1 + rs))
    # float にして返す
    return float(rsi.iloc[-1])

@functools.lru_cache(maxsize=1)
def _fetch_fgi():
    key = os.environ.get("RAPIDAPI_KEY", "")
    url = "https://fear-and-greed-index.p.rapidapi.com/v1/fgi"
    headers = {
        "X-RapidAPI-Key": key,
        "X-RapidAPI-Host": "fear-and-greed-index.p.rapidapi.com"
    }
    return requests.get(url, headers=headers, timeout=5).json()

@app.route('/api/health')
def health():
    return jsonify({"status":"ok"})

@app.route('/api/fear_greed')
def fg():
    return jsonify(_fetch_fgi())

@app.route('/api/ndx_change')
def ndx_change():
    # 2週間分のデータを取得
    df = yf.download(
        "^NDX",
        start=(datetime.today() - timedelta(days=14)).strftime('%Y-%m-%d'),
        end=datetime.today().strftime('%Y-%m-%d'),
        progress=False
    )
    df.index = pd.to_datetime(df.index)
    fridays = df[df.index.weekday == 4]
    if len(fridays) < 2:
        return jsonify({"error": "データ不足"}), 500

    # 先週と今週の金曜日を取り出し、プリミティブ型に変換
    prev_row = fridays.iloc[-2]
    last_row = fridays.iloc[-1]

    prev_date = fridays.index[-2].strftime('%Y-%m-%d')
    last_date = fridays.index[-1].strftime('%Y-%m-%d')
    prev_close = float(prev_row["Close"])
    last_close = float(last_row["Close"])
    pct_change = round((last_close - prev_close) / prev_close * 100, 2)

    return jsonify({
        "prev_date": prev_date,
        "last_date": last_date,
        "prev_close": prev_close,
        "last_close": last_close,
        "pct_change": pct_change
    })
@app.route('/api/market_data')
def market_data():
    # symbols クエリがなければデフォルト4つ
    qs = request.args.get("symbols", "")
    symbols = qs.split(",") if qs else ["^NDX", "^SOX", "XLK", "^VIX"]

    df = _load_data(tuple(symbols))
    if df.empty:
        return jsonify({"error": "データ取得失敗"}), 500

    # 日付文字列に変換
    dates = df.index[-5:]
    prev_date = dates[-2].strftime('%Y-%m-%d')
    last_date = dates[-1].strftime('%Y-%m-%d')

    response = {}
    for sym in symbols:
        if sym not in df.columns:
            continue
        prev_val = float(df.loc[prev_date, sym])
        last_val = float(df.loc[last_date, sym])
        pct_change = round((last_val - prev_val) / prev_val * 100, 2)
        rsi_val = round(calculate_rsi(df[sym]), 2)

        response[sym] = {
            "prev_date": prev_date,
            "last_date": last_date,
            "prev_close": prev_val,
            "last_close": last_val,
            "pct_change": pct_change,
            "rsi": rsi_val
        }

    return jsonify(response)

# NAAIM Exposure Index
from naaim import handler as naaim_handler
@app.route('/api/naaim')
def naaim_endpoint():
    # handler に Flask の request を渡す
    result = naaim_handler(request)
    return jsonify(result)
if __name__ == '__main__':
    app.run(port=5000, debug=True)

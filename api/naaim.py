# api/naaim.py
import os
import requests
from datetime import datetime

def handler(request):
    api_key = os.environ.get("NASDAQ_DATA_LINK_KEY")
    if not api_key:
        return {"error": "NASDAQ_DATA_LINK_KEY が未設定です"}

    # Nasdaq Data Link API URL
    url = "https://data.nasdaq.com/api/v3/datasets/NAAIM/NAAIM.json"
    params = {"api_key": api_key}

    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        payload = resp.json().get("dataset", {})
        series = payload.get("data", [])

        if not series:
            return {"error": "データが見つかりませんでした"}

        # 最新2件を取得
        latest_date_str, latest_value = series[0][0], series[0][1]
        if len(series) > 1:
            prev_date_str, prev_value = series[1][0], series[1][1]
        else:
            prev_date_str, prev_value = None, None

        # 日付文字列をパースしてISO形式に
        try:
            latest_date = datetime.strptime(latest_date_str, "%Y-%m-%d").isoformat()
        except Exception:
            latest_date = latest_date_str
        try:
            prev_date = (
                datetime.strptime(prev_date_str, "%Y-%m-%d").isoformat()
                if prev_date_str
                else None
            )
        except Exception:
            prev_date = prev_date_str

        # プリミティブ型にキャストして返却
        return {
            "latest_date": latest_date,
            "latest_value": float(latest_value),
            "prev_date": prev_date,
            "prev_value": float(prev_value) if prev_value is not None else None,
        }

    except requests.RequestException as e:
        return {"error": f"データ取得エラー: {e}"}
    except Exception as e:
        return {"error": f"予期しないエラー: {e}"}

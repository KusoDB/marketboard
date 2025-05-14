import os
import requests

def handler(request):
    # RapidAPI のキーを環境変数から取得
    api_key = os.getenv("RAPIDAPI_KEY")
    if not api_key:
        return {"error": "RAPIDAPI_KEY が未設定です"}, 500

    url = "https://fear-and-greed-index-api.p.rapidapi.com/index"
    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": "fear-and-greed-index-api.p.rapidapi.com"
    }

    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
    except requests.RequestException as e:
        return {"error": f"API リクエスト失敗: {e}"}, 500

    data = resp.json()
    # 必要なフィールドだけを抜き出して返却
    return {
        "value": data.get("value"),
        "classification": data.get("classification"),
        "timestamp": data.get("timestamp")
    }

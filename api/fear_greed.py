# api/fear_greed.py
import os
import functools
import requests

@functools.lru_cache(maxsize=1)
def _fetch_fgi():
    key = os.environ.get("RAPIDAPI_KEY")
    url = "https://fear-and-greed-index.p.rapidapi.com/v1/fgi"
    headers = {
        "X-RapidAPI-Key": key,
        "X-RapidAPI-Host": "fear-and-greed-index.p.rapidapi.com"
    }
    return requests.get(url, headers=headers, timeout=5).json()

def handler(request):
    # dict を返せば Vercel が自動で JSON レスポンスとして返してくれます
    return _fetch_fgi()

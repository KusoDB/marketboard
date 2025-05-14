# api/health.py
def handler(request):
    # dict を返せば自動的に JSON レスポンスになります
    return {"status": "ok"}

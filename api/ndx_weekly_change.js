// api/ndx_weekly_change.js
let cache = { data: null, fetchedAt: 0 };
const TTL = 5 * 60 * 1000; // キャッシュ有効期間：5分

export default async function handler(req, res) {
  const now = Date.now();
  if (cache.data && now - cache.fetchedAt < TTL) {
    return res.json(cache.data);
  }

  const key = process.env.RAPIDAPI_KEY;
  if (!key) {
    return res.status(500).json({ error: 'RAPIDAPI_KEY が未設定です' });
  }

  // 1週間前と現在の UNIX タイムスタンプ（秒）
  const period1 = Math.floor((Date.now() - 7 * 24 * 3600 * 1000) / 1000);
  const period2 = Math.floor(Date.now() / 1000);
  const url = `https://yh-finance.p.rapidapi.com/market/get-history?symbol=%5ENDX&period1=${period1}&period2=${period2}&interval=1d`;

  try {
    const r = await fetch(url, {
      headers: {
        'X-RapidAPI-Key': key,
        'X-RapidAPI-Host': 'yh-finance.p.rapidapi.com'
      }
    });
    if (!r.ok) throw new Error(`${r.status} ${r.statusText}`);
    const json = await r.json();
    const prices = (json.prices || []).filter(p => p.close != null);
    if (prices.length < 2) {
      throw new Error('十分なデータが取得できませんでした');
    }
    const first = prices[0].close;
    const last  = prices[prices.length - 1].close;
    const changePercent = parseFloat((((last - first) / first) * 100).toFixed(2));

    const result = { weekly_change_percent: changePercent };
    cache = { data: result, fetchedAt: now };
    return res.json(result);
  } catch (e) {
    return res.status(500).json({ error: `データ取得失敗: ${e.message}` });
  }
}

// api/ndx_weekly_change.js
let cache = { data: null, fetchedAt: 0 };
const TTL = 5 * 60 * 1000; // 5分

export default async function handler(req, res) {
  const now = Date.now();
  if (cache.data && now - cache.fetchedAt < TTL) {
    return res.json(cache.data);
  }

  const url =
    'https://query1.finance.yahoo.com/v8/finance/chart/%5ENDX?range=7d&interval=1d&includePrePost=false';

  try {
    const r = await fetch(url);
    if (!r.ok) throw new Error(`${r.status} ${r.statusText}`);
    const json = await r.json();
    const resultData = json.chart?.result?.[0];
    if (!resultData) throw new Error('データ形式が予期せぬ構造です');

    const closes =
      resultData.indicators.quote[0].close.filter((c) => c !== null);
    if (closes.length < 2) {
      throw new Error('十分な終値データが取得できませんでした');
    }

    const first = closes[0];
    const last = closes[closes.length - 1];
    const changePercent = parseFloat(
      (((last - first) / first) * 100).toFixed(2)
    );

    const payload = { weekly_change_percent: changePercent };
    cache = { data: payload, fetchedAt: now };
    return res.json(payload);
  } catch (e) {
    return res
      .status(500)
      .json({ error: `データ取得失敗: ${e.message}` });
  }
}

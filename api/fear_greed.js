// api/fear_greed.js
let cache = {
  data: null,
  fetchedAt: 0
};
const TTL =  5 * 60 * 1000; // 5 分

export default async function handler(req, res) {
  const now = Date.now();
  if (cache.data && now - cache.fetchedAt < TTL) {
    // キャッシュが有効なら即返却
    return res.json(cache.data);
  }

  // ここから本番 fetch
  const key = process.env.RAPIDAPI_KEY;
  if (!key) {
    return res.status(500).json({ error: 'RAPIDAPI_KEY が未設定です' });
  }
  const url = 'https://fear-and-greed-index-api.p.rapidapi.com/index';

  try {
    const r = await fetch(url, {
      headers: {
        'X-RapidAPI-Key': key,
        'X-RapidAPI-Host': 'fear-and-greed-index-api.p.rapidapi.com'
      }
    });
    if (!r.ok) throw new Error(`${r.status} ${r.statusText}`);
    const json = await r.json();
    const result = {
      value: json.value,
      classification: json.classification,
      timestamp: json.timestamp
    };
    // キャッシュ更新
    cache = { data: result, fetchedAt: now };
    return res.json(result);
  } catch (e) {
    return res
      .status(500)
      .json({ error: `API リクエスト失敗: ${e.message}` });
  }
}

// api/fear_greed.js
export default async function handler(req, res) {
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
    const data = await r.json();
    return res.json({
      value: data.value,
      classification: data.classification,
      timestamp: data.timestamp
    });
  } catch (e) {
    return res.status(500).json({ error: `API リクエスト失敗: ${e.message}` });
  }
}

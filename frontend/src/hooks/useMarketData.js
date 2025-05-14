import { useQuery } from '@tanstack/react-query';
export default function useMarketData(symbols) {
  const key = symbols ? symbols.join(',') : '';
  return useQuery(['marketData', key], ()=>(
    fetch(`/api/market_data?symbols=${key}`).then(r=>r.json())
  ), { staleTime:900000 });
}
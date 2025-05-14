import { useQuery } from '@tanstack/react-query';
export default function useFearGreed() {
  return useQuery(['fearGreed'], ()=>(
    fetch('/api/fear_greed').then(r=>r.json())
  ), { staleTime:900000 });
}
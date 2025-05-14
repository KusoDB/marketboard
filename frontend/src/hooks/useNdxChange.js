import { useQuery } from '@tanstack/react-query';
export default function useNdxChange() {
  return useQuery(['ndxChange'], ()=>(
    fetch('/api/ndx_change').then(r=>r.json())
  ), { staleTime:900000 });
}
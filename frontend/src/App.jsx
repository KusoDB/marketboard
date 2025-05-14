// frontend/src/App.jsx
import React from 'react';
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js';
ChartJS.register(ArcElement, Tooltip, Legend);

import useFearGreed from './hooks/useFearGreed';
import useNdxChange from './hooks/useNdxChange';
import useMarketData from './hooks/useMarketData';
import { Doughnut } from 'react-chartjs-2';

export default function App() {
  const { data: fgi, isLoading: loadingFgi } = useFearGreed();
  const { data: ndx, isLoading: loadingNdx } = useNdxChange();
  const { data: market, isLoading: loadingMarket } = useMarketData();

  console.log("FGI:", fgi);
  console.log("NDX:", ndx);
  console.log("Market:", market);

  if (loadingFgi || loadingNdx || loadingMarket) {
    return <p className="text-center mt-8">Loading…</p>;
  }

  return (
    <div className="container mx-auto p-4 space-y-8">
      {/* Fear & Greed Index */}
      <section className="text-center">
        <h2 className="text-2xl font-semibold mb-4">Fear & Greed Index</h2>
        <div className="mx-auto max-w-xs">
          <Doughnut
            data={{
              labels: ['Index', 'Remaining'],
              datasets: [{
                data: [fgi.fgi.now.value, 100 - fgi.fgi.now.value],
                backgroundColor: ['#008000', '#E0E0E0'],
                borderWidth: 0
              }]
            }}
            options={{
              circumference: 180,
              rotation: 270,
              cutout: '80%',
              plugins: { tooltip: { enabled: false } }
            }}
          />
        </div>
        <p className="mt-2 text-xl">
          {fgi.fgi.now.value} — {fgi.fgi.now.valueText}
        </p>
      </section>

      {/* NDX Change */}
      <section className="text-center">
        <h2 className="text-2xl font-semibold mb-4">NDX Change</h2>
        <p className="text-lg">
          {ndx.prev_date.replace(/-/g, '/')} → {ndx.last_date.replace(/-/g, '/')} :{' '}
          <span className={ndx.pct_change > 0 ? 'text-green-600' : 'text-red-600'}>
            {ndx.pct_change}%
          </span>
        </p>
      </section>

      {/* Market Data Table */}
      <section>
        <h2 className="text-2xl font-semibold mb-4 text-center">Market Data</h2>
        <div className="overflow-x-auto">
          <table className="min-w-full border-collapse">
            <thead>
              <tr>
                <th className="border px-4 py-2">Symbol</th>
                <th className="border px-4 py-2">Prev ({market['^NDX'].prev_date.replace(/-/g,'/')})</th>
                <th className="border px-4 py-2">Last ({market['^NDX'].last_date.replace(/-/g,'/')})</th>
                <th className="border px-4 py-2">%</th>
                <th className="border px-4 py-2">RSI</th>
              </tr>
            </thead>
            <tbody>
              {Object.entries(market).map(([sym, info]) => (
                <tr key={sym} className="text-center">
                  <td className="border px-4 py-2">{sym.replace('^', '')}</td>
                  <td className="border px-4 py-2">{info.prev_close}</td>
                  <td className="border px-4 py-2">{info.last_close}</td>
                  <td className={`border px-4 py-2 ${info.pct_change > 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {info.pct_change}%
                  </td>
                  <td className={`border px-4 py-2 ${
                    info.rsi < 30 ? 'text-red-600' :
                    info.rsi < 40 ? 'text-yellow-500' :
                    info.rsi < 60 ? '' :
                    info.rsi < 70 ? 'text-yellow-500' :
                    'text-red-600'
                  }`}>
                    {info.rsi}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}

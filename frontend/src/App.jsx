import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import axios from 'axios';

const API_URL = "http://localhost:8000";

export default function App() {
  const [minConviction, setMinConviction] = useState(0);

  const { data: signals } = useQuery({
    queryKey: ['signals', minConviction],
    queryFn: async () => {
      const { data } = await axios.get(`${API_URL}/signals?min_conviction=${minConviction}`);
      return data;
    },
    refetchInterval: 30000, // Refresh every 30s per roadmap 
  });

  const { data: topMovers } = useQuery({
    queryKey: ['top-movers'],
    queryFn: async () => {
      const { data } = await axios.get(`${API_URL}/top-movers`);
      return data;
    },
  });

  return (
    <div className="flex h-screen bg-slate-950 text-white font-sans">
      {/* SIDEBAR NAVIGATION  */}
      <aside className="w-64 border-r border-slate-800 p-6 flex flex-col gap-6">
        <h1 className="text-xl font-bold text-blue-500">Smart Money Engine</h1>
        <nav className="flex flex-col gap-4">
          <button onClick={() => setMinConviction(0)} className="text-left hover:text-blue-400">📡 Signal Feed</button>
          <div className="mt-4">
            <p className="text-xs text-slate-500 uppercase mb-2">Top Movers Today</p>
            {topMovers?.map((m, i) => (
              <div key={i} className="text-sm py-1 border-b border-slate-800 flex justify-between">
                <span>{m.token}</span>
                <span className="text-emerald-400">{m.count} wallets</span>
              </div>
            ))}
          </div>
        </nav>
      </aside>

      {/* MAIN FEED */}
      <main className="flex-1 p-8 overflow-auto">
        <header className="flex justify-between items-center mb-8">
          <h2 className="text-3xl font-bold">Live Signals</h2>
          {/* FILTER BAR  */}
          <div className="flex gap-2 bg-slate-900 p-1 rounded-lg">
            {[
              { label: 'ALL', val: 0 },
              { label: 'HIGH', val: 70 },
              { label: 'MED', val: 40 },
              { label: 'LOW', val: 1 }
            ].map((f) => (
              <button 
                key={f.label}
                onClick={() => setMinConviction(f.val)}
                className={`px-4 py-1 rounded-md text-xs font-bold ${minConviction === f.val ? 'bg-blue-600' : 'hover:bg-slate-800'}`}
              >
                {f.label}
              </button>
            ))}
          </div>
        </header>

        {/* SIGNAL LIST  */}
        <div className="grid gap-4">
          {signals?.map((s, i) => (
            <div key={i} className="bg-slate-900 border border-slate-800 p-4 rounded-xl flex justify-between items-center">
              <div>
                <h3 className="text-xl font-bold">${s.token}</h3>
                <p className="text-slate-500 text-sm">{s.signal_type} • {s.wallets_involved}</p>
              </div>
              <div className={`px-4 py-2 rounded font-black ${s.conviction_score >= 70 ? 'text-emerald-400 bg-emerald-400/10' : 'text-yellow-400 bg-yellow-400/10'}`}>
                {s.conviction_score}/100
              </div>
            </div>
          ))}
        </div>
      </main>
    </div>
  );
}
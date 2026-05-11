import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import axios from 'axios';

const API_URL = "http://localhost:8000";

export default function App() {
  const [filter, setFilter] = useState(0);

  const { data: signals, isLoading } = useQuery({
    queryKey: ['signals', filter],
    queryFn: async () => {
      const { data } = await axios.get(`${API_URL}/signals?min_conviction=${filter}`);
      return data;
    },
    refetchInterval: 10000, // Refresh every 10 seconds
  });

  return (
    <div className="flex h-screen bg-slate-950 text-slate-100">
      {/* SIDEBAR */}
      <aside className="w-64 border-r border-slate-800 p-6 flex flex-col gap-8">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-blue-600 rounded-lg shadow-lg shadow-blue-500/50"></div>
          <h1 className="font-black text-xl tracking-tighter">SMART MONEY</h1>
        </div>
        <nav className="flex flex-col gap-2">
          <button className="text-left px-4 py-2 bg-slate-900 text-blue-400 rounded-xl font-bold">📡 Live Feed</button>
          <button className="text-left px-4 py-2 hover:bg-slate-900 rounded-xl text-slate-500">🐋 Whale Watch</button>
        </nav>
      </aside>

      {/* MAIN FEED */}
      <main className="flex-1 p-8 overflow-y-auto">
        <header className="flex justify-between items-center mb-10">
          <div>
            <h2 className="text-3xl font-bold">Signal Feed</h2>
            <p className="text-slate-500">Real-time on-chain intelligence</p>
          </div>
          
          {/* FILTER BUTTONS */}
          <div className="flex gap-2 bg-slate-900 p-1 rounded-xl border border-slate-800">
            {[{l:'ALL', v:0}, {l:'HIGH', v:70}, {l:'MED', v:40}].map((f) => (
              <button 
                key={f.l} 
                onClick={() => setFilter(f.v)}
                className={`px-6 py-1.5 rounded-lg text-xs font-black transition-all ${filter === f.v ? 'bg-blue-600 text-white shadow-lg' : 'text-slate-500 hover:text-slate-300'}`}
              >
                {f.l}
              </button>
            ))}
          </div>
        </header>

        {/* SIGNAL CARDS */}
        <div className="grid gap-4">
          {isLoading ? (
            <div className="text-center py-20 text-slate-500 animate-pulse">Scanning liquidity pools...</div>
          ) : signals?.map((s, i) => (
            <div key={i} className="bg-slate-900/50 border border-slate-800 p-5 rounded-2xl flex justify-between items-center hover:border-blue-500/50 transition-colors">
              <div className="flex items-center gap-5">
                <div className="w-12 h-12 bg-slate-800 rounded-full flex items-center justify-center text-xl font-bold text-blue-400 border border-slate-700">
                  {s.token[0]}
                </div>
                <div>
                  <h3 className="text-xl font-black">${s.token}</h3>
                  <p className="text-sm text-slate-500 font-mono">{s.wallets_involved}</p>
                </div>
              </div>
              <div className="text-right">
                <span className={`text-xs font-black px-3 py-1 rounded-full border ${s.conviction_score >= 70 ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' : 'bg-blue-500/10 text-blue-400 border-blue-500/20'}`}>
                  {s.conviction_score}/100 CONVICTION
                </span>
                <p className="text-xs text-slate-600 mt-2">Detected: Just Now</p>
              </div>
            </div>
          ))}
        </div>
      </main>
    </div>
  );
}
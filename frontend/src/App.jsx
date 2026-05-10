import React from 'react';
import { useQuery } from '@tanstack/react-query';
import axios from 'axios';

// API Fetcher - Ensure your FastAPI is running on port 8000!
const fetchSignals = async () => {
  const { data } = await axios.get('http://localhost:8000/signals');
  return data;
};

function App() {
  const { data: signals, isLoading, error } = useQuery({
    queryKey: ['signals'],
    queryFn: fetchSignals,
    refetchInterval: 10000, // Auto-refresh every 10 seconds
  });

  return (
    <div className="min-h-screen p-8 bg-slate-950 text-slate-100">
      <header className="max-w-6xl mx-auto mb-12 flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-blue-400 tracking-tight">
            Smart Money Engine
          </h1>
          <p className="text-slate-500 text-sm">On-chain signals & liquidity alerts</p>
        </div>
        <div className="flex items-center gap-2 px-3 py-1 bg-green-500/10 border border-green-500/20 rounded-full">
          <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
          <span className="text-xs font-medium text-green-400 uppercase">Live</span>
        </div>
      </header>

      <main className="max-w-6xl mx-auto">
        {isLoading ? (
          <div className="text-center py-20 text-slate-600 animate-pulse">Scanning liquidity pools...</div>
        ) : error ? (
          <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-lg text-red-400 text-sm">
            Backend Offline: Ensure FastAPI is running at localhost:8000
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {signals?.map((signal) => (
              <div key={signal.id} className="p-6 bg-slate-900 border border-slate-800 rounded-xl hover:border-blue-500/50 transition-colors shadow-2xl">
                <div className="flex justify-between items-start mb-4">
                  <h2 className="text-xl font-bold text-white">${signal.token}</h2>
                  <span className="text-[10px] font-bold px-2 py-1 bg-blue-500/10 text-blue-400 border border-blue-500/20 rounded uppercase">
                    {signal.signal_type}
                  </span>
                </div>
                
                <div className="space-y-3">
                  <div className="flex justify-between text-sm">
                    <span className="text-slate-500">Conviction</span>
                    <span className="text-blue-300 font-mono">{signal.conviction_score}%</span>
                  </div>
                  <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
                    <div 
                      className="bg-blue-500 h-full transition-all duration-1000" 
                      style={{ width: `${signal.conviction_score}%` }}
                    />
                  </div>
                  <p className="text-sm text-slate-400 mt-4 leading-relaxed italic">
                    "{signal.wallets_involved}"
                  </p>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
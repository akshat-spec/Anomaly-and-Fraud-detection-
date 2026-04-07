import React, { useEffect, useState } from "react";
import { Area, XAxis, YAxis, Tooltip, ResponsiveContainer, Bar, ComposedChart } from "recharts";


// Mock implementation assuming the backend /stats endpoint can return timeseries arrays,
// or we build it natively from the websocket. 
// For this Phase, we'll poll or simulate 60 minutes of data for the design.
export const FraudRateChart: React.FC = () => {
  const [data, setData] = useState<any[]>([]);

  useEffect(() => {
    // Simulated realistic 60 minute timeseries buckets
    const generateData = () => {
      const series = [];
      const now = new Date();
      for (let i = 60; i >= 0; i--) {
        const time = new Date(now.getTime() - i * 60000);
        series.push({
          time: time.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          volume: Math.floor(Math.random() * 50) + 10,
          fraudRate: Math.random() > 0.8 ? +(Math.random() * 5).toFixed(1) : +(Math.random() * 1).toFixed(1)
        });
      }
      setData(series);
    };

    generateData();
    const interval = setInterval(generateData, 30000); // refresh every 30s
    return () => clearInterval(interval);
  }, []);

  if (!data.length) {
    return <div className="h-[300px] w-full bg-[#111111] animate-pulse rounded-xl" />;
  }

  return (
    <div className="flex flex-col bg-[#111111] border border-gray-800 rounded-xl p-5 shadow-2xl h-[340px]">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-gray-100 font-semibold tracking-tight">System Throughput & Integrity</h2>
          <p className="text-xs text-gray-500 mt-1">Transaction volume vs identified anomaly rate</p>
        </div>
        <div className="flex items-center gap-2 px-3 py-1 bg-gray-900 rounded border border-gray-800 shadow-inner">
          <span className="w-2 h-2 rounded-full bg-purple-500"></span>
          <span className="text-xs font-mono text-gray-400">Volume</span>
          <span className="w-2 h-2 rounded-full bg-red-500 ml-2"></span>
          <span className="text-xs font-mono text-gray-400">Fraud Rate %</span>
        </div>
      </div>

      <div className="flex-1 min-h-0 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={data} margin={{ top: 0, right: 0, bottom: 0, left: -20 }}>
            <defs>
              <linearGradient id="colorFraud" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#ef4444" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#ef4444" stopOpacity={0} />
              </linearGradient>
            </defs>
            <XAxis dataKey="time" stroke="#374151" fontSize={11} tickMargin={10} minTickGap={30} />
            <YAxis yAxisId="left" stroke="#374151" fontSize={11} tickFormatter={(v) => `${v}`} />
            <YAxis yAxisId="right" orientation="right" stroke="#374151" fontSize={11} tickFormatter={(v) => `${v}%`} />
            <Tooltip 
              contentStyle={{ backgroundColor: '#18181b', borderColor: '#27272a', borderRadius: '8px', color: '#f4f4f5', boxShadow: '0 10px 15px -3px rgb(0 0 0 / 0.5)' }} 
              itemStyle={{ fontSize: '13px' }}
              labelStyle={{ color: '#a1a1aa', fontSize: '12px', marginBottom: '4px' }}
            />
            <Bar yAxisId="left" dataKey="volume" fill="#8b5cf6" radius={[2, 2, 0, 0]} opacity={0.5} maxBarSize={15} />
            <Area yAxisId="right" type="monotone" dataKey="fraudRate" stroke="#ef4444" strokeWidth={2} fillOpacity={1} fill="url(#colorFraud)" />
          </ComposedChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

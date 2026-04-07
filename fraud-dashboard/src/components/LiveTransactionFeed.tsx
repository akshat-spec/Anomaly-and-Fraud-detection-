import React, { useState } from "react";
import { FixedSizeList as List } from "react-window";
import { Play, Pause, AlertTriangle, ShieldCheck, Activity } from "lucide-react";
import { useWebSocket } from "../hooks/useWebSocket";
import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export const LiveTransactionFeed: React.FC = () => {
  const { messages, isConnected, isPaused, togglePause } = useWebSocket();
  const [showFraudOnly, setShowFraudOnly] = useState(false);

  const filteredMessages = showFraudOnly
    ? messages.filter((m) => m.fraud || m.confidence > 0.7) // Aggressive filter
    : messages;

  const Row = ({ index, style }: { index: number; style: React.CSSProperties }) => {
    const txn = filteredMessages[index];
    if (!txn) return null;

    const isFraud = txn.fraud || txn.confidence > 0.7;

    return (
      <div style={style} className="px-4 py-2 border-b border-gray-800 hover:bg-gray-800 transition-colors flex items-center justify-between text-sm">
        <div className="flex items-center gap-4 w-1/3">
          <div className={cn("p-2 rounded-full", isFraud ? "bg-red-500/20 text-red-500" : "bg-emerald-500/20 text-emerald-500")}>
            {isFraud ? <AlertTriangle size={16} /> : <ShieldCheck size={16} />}
          </div>
          <div>
            <div className="font-mono text-gray-300 w-32 truncate">{txn.transaction_id.substring(0, 12)}...</div>
            <div className="text-xs text-gray-500">{txn.user_id}</div>
          </div>
        </div>

        <div className="w-1/4 text-right font-medium text-gray-200">
          ${Number(txn.amount).toFixed(2)}
        </div>

        <div className="w-1/4 flex flex-col items-end">
          <span className={cn("font-bold", isFraud ? "text-red-400" : "text-emerald-400")}>
            {(txn.confidence * 100).toFixed(1)}% Conf
          </span>
          <span className="text-xs text-gray-500 flex items-center gap-1">
            <Activity size={10} /> {Math.round(txn.latency_ms || 0)}ms
          </span>
        </div>
      </div>
    );
  };

  return (
    <div className="flex flex-col h-[500px] w-full bg-[#111111] border border-gray-800 rounded-xl overflow-hidden shadow-2xl">
      <div className="flex items-center justify-between p-4 border-b border-gray-800 bg-[#161616]">
        <div className="flex items-center gap-3">
          <div className="relative flex h-3 w-3">
            <span className={cn("animate-ping absolute inline-flex h-full w-full rounded-full opacity-75", isConnected ? "bg-emerald-400" : "bg-red-400")}></span>
            <span className={cn("relative inline-flex rounded-full h-3 w-3", isConnected ? "bg-emerald-500" : "bg-red-500")}></span>
          </div>
          <h2 className="text-gray-100 font-semibold tracking-tight">Live Firehose</h2>
          <span className="text-xs px-2 py-1 bg-gray-800 text-gray-400 rounded-md font-mono">{filteredMessages.length} events</span>
        </div>
        
        <div className="flex items-center gap-3">
          <label className="flex items-center gap-2 text-xs text-gray-400 cursor-pointer hover:text-gray-200 transition-colors">
            <input 
              type="checkbox" 
              checked={showFraudOnly} 
              onChange={() => setShowFraudOnly(!showFraudOnly)} 
              className="rounded bg-gray-900 border-gray-700 text-purple-500 focus:ring-purple-500/20"
            />
            Fraud Only
          </label>
          <div className="h-4 w-px bg-gray-800 mx-1 border-gray-700"></div>
          <button 
            onClick={togglePause} 
            className="flex items-center gap-1.5 text-xs px-3 py-1.5 bg-gray-800 hover:bg-gray-700 text-gray-300 rounded-md transition-colors"
          >
            {isPaused ? <Play size={14} className="text-emerald-400" /> : <Pause size={14} className="text-amber-400" />}
            {isPaused ? "Resume" : "Pause"}
          </button>
        </div>
      </div>

      <div className="flex-1 bg-[#0a0a0a]">
        {filteredMessages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-gray-600 animate-pulse">
            <Activity size={32} className="mb-3 opacity-20" />
            <p className="text-sm tracking-widest uppercase">Listening for signals...</p>
          </div>
        ) : (
          <List
            height={435}
            itemCount={filteredMessages.length}
            itemSize={60}
            width="100%"
            className="scrollbar-thin scrollbar-thumb-gray-800 scrollbar-track-transparent"
          >
            {Row}
          </List>
        )}
      </div>
    </div>
  );
};

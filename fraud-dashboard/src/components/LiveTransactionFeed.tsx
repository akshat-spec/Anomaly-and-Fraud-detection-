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
    <div className="flex flex-col h-[500px] w-full bg-[#0a0a0a] border border-white/5 rounded-2xl overflow-hidden shadow-2xl">
      <div className="flex items-center justify-between p-5 border-b border-white/5 bg-black/40 backdrop-blur-md">
        <div className="flex items-center gap-4">
          <div className="relative flex h-2.5 w-2.5">
            <span className={cn("animate-ping absolute inline-flex h-full w-full rounded-full opacity-75", isConnected ? "bg-emerald-400" : "bg-red-400")}></span>
            <span className={cn("relative inline-flex rounded-full h-2.5 w-2.5", isConnected ? "bg-emerald-500" : "bg-red-500")}></span>
          </div>
          <div>
            <h2 className="text-white text-sm font-bold tracking-tight">Live Firehose</h2>
            <p className="text-[10px] text-gray-500 font-medium uppercase tracking-wider">{filteredMessages.length} Signal Stream</p>
          </div>
        </div>
        
        <div className="flex items-center gap-4">
          <label className="flex items-center gap-2 text-[11px] text-gray-400 cursor-pointer hover:text-white transition-colors">
            <input 
              type="checkbox" 
              checked={showFraudOnly} 
              onChange={() => setShowFraudOnly(!showFraudOnly)} 
              className="rounded-sm bg-black border-white/10 text-indigo-500 focus:ring-indigo-500/20 w-3.5 h-3.5"
            />
            FRAUD ONLY
          </label>
          <div className="h-4 w-px bg-white/10"></div>
          <button 
            onClick={togglePause} 
            className="flex items-center gap-2 text-[10px] font-bold uppercase tracking-widest px-4 py-2 bg-white/5 hover:bg-white/10 text-gray-300 rounded-lg border border-white/5 transition-all active:scale-95"
          >
            {isPaused ? <Play size={12} className="fill-emerald-400 text-emerald-400" /> : <Pause size={12} className="fill-amber-400 text-amber-400" />}
            {isPaused ? "Resume" : "Pause"}
          </button>
        </div>
      </div>

      <div className="flex-1 bg-black">
        {filteredMessages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-gray-700 animate-pulse">
            <Activity size={40} className="mb-4 opacity-10" />
            <p className="text-xs font-bold tracking-[0.3em] uppercase opacity-40">Awaiting Signal...</p>
          </div>
        ) : (
          <List
            height={435}
            itemCount={filteredMessages.length}
            itemSize={64}
            width="100%"
            className="scrollbar-thin scrollbar-thumb-white/5 scrollbar-track-transparent"
          >
            {Row}
          </List>
        )}
      </div>
    </div>
  );
};

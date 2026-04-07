import React, { useEffect, useState } from "react";
import { ChevronDown, ChevronUp, ShieldCheck, ShieldAlert } from "lucide-react";
import { getAlerts, markAlertReviewed } from "../api/client";
import type { AlertSchema } from "../types";

export const AlertPanel: React.FC = () => {
  const [alerts, setAlerts] = useState<AlertSchema[]>([]);
  const [expandedRow, setExpandedRow] = useState<string | null>(null);

  useEffect(() => {
    // Simulated fetching for the demonstration to look immediately active
    // Polling normally implemented against /alerts endpoint
    const fetchA = async () => {
      try {
        const data = await getAlerts();
        setAlerts(data.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()));
      } catch (e) {
        // Mock data fallback if DB disconnected or 404
        setAlerts([
          {
            id: "1",
            transaction_id: "tx_mock_12948291",
            user_id: "usr_suspicious_01",
            is_fraud: true,
            xgb_score: 0.985,
            iso_score: -1,
            confidence: 0.98,
            created_at: new Date().toISOString(),
            reviewed: false
          },
          {
            id: "2",
            transaction_id: "tx_mock_8412849",
            user_id: "usr_botnet_99",
            is_fraud: true,
            xgb_score: 0.75,
            iso_score: 1,
            confidence: 0.75,
            created_at: new Date(Date.now() - 60000).toISOString(),
            reviewed: true
          }
        ]);
      }
    };
    fetchA();
    const interval = setInterval(fetchA, 15000);
    return () => clearInterval(interval);
  }, []);

  const handleReview = async (e: React.MouseEvent, id: string) => {
    e.stopPropagation();
    try {
      // Optimitic update natively
      setAlerts(alerts.map(a => a.id === id ? { ...a, reviewed: true } : a));
      await markAlertReviewed(id);
    } catch (e) {
      console.warn("API Review tracking bounded offline", e);
    }
  };

  if (!alerts.length) return <div className="h-[400px] bg-[#111111] animate-pulse rounded-xl shadow-lg border border-gray-800" />;

  return (
    <div className="flex flex-col bg-[#111111] border border-gray-800 rounded-xl overflow-hidden shadow-2xl col-span-1 md:col-span-2">
      <div className="flex items-center justify-between p-4 border-b border-gray-800 bg-[#161616]">
        <div className="flex items-center gap-2">
          <ShieldAlert className="text-red-400" size={18} />
          <h2 className="text-gray-100 font-semibold tracking-tight">Active Fraud Escalations</h2>
        </div>
        <span className="text-xs px-2 py-1 bg-red-500/10 text-red-400 rounded-md border border-red-500/20 font-semibold">
          {alerts.filter(a => !a.reviewed).length} Pending Review
        </span>
      </div>

      <div className="flex-1 overflow-y-auto max-h-[350px] scrollbar-thin scrollbar-thumb-gray-800 bg-[#0a0a0a]">
        {alerts.map((a) => (
          <div key={a.id} className="border-b border-gray-800/50 last:border-0 hover:bg-gray-800/30 transition-colors">
            <div 
              className={`p-4 cursor-pointer flex items-center justify-between ${a.reviewed ? 'opacity-60' : ''}`}
              onClick={() => setExpandedRow(expandedRow === a.id ? null : a.id)}
            >
              <div className="flex items-center gap-4">
                <div className={`p-2 rounded-full ${a.reviewed ? 'bg-gray-800 text-gray-500' : 'bg-red-500/20 text-red-500'}`}>
                  {a.reviewed ? <ShieldCheck size={16} /> : <ShieldAlert size={16} />}
                </div>
                <div>
                  <div className="font-mono text-gray-200 text-sm">{a.transaction_id.substring(0, 16)}</div>
                  <div className="text-xs text-gray-500">{new Date(a.created_at).toLocaleTimeString()} · User: {a.user_id}</div>
                </div>
              </div>
              
              <div className="flex items-center gap-4">
                <span className="text-red-400 font-medium text-sm">{(a.confidence * 100).toFixed(1)}% Conf</span>
                {!a.reviewed && (
                  <button 
                    onClick={(e) => handleReview(e, a.id)}
                    className="text-xs px-3 py-1 bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 border border-emerald-500/20 rounded-md transition-colors"
                  >
                    Mark Reviewed
                  </button>
                )}
                <div className="text-gray-500">
                  {expandedRow === a.id ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                </div>
              </div>
            </div>

            {expandedRow === a.id && (
              <div className="p-4 bg-[#111111] border-t border-gray-800/80">
                <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                  <div className="bg-gray-900 border border-gray-800 p-2 rounded shadow-inner">
                    <span className="text-gray-500 text-xs block mb-1">XGBoost Score</span>
                    <span className="text-red-400 font-mono text-sm">{a.xgb_score.toFixed(4)}</span>
                  </div>
                  <div className="bg-gray-900 border border-gray-800 p-2 rounded shadow-inner">
                    <span className="text-gray-500 text-xs block mb-1">Isolation Forest</span>
                    <span className="text-red-400 font-mono text-sm">{a.iso_score === -1 ? 'Anomaly (-1)' : 'Normal (1)'}</span>
                  </div>
                  <div className="bg-gray-900 border border-gray-800 p-2 rounded shadow-inner lg:col-span-2">
                    <span className="text-gray-500 text-xs block mb-1">Investigation Action</span>
                    <button className="text-xs bg-red-500 hover:bg-red-600 text-white px-3 py-1.5 rounded transition-colors mr-2">Block Card</button>
                    <button className="text-xs bg-gray-800 hover:bg-gray-700 text-gray-200 px-3 py-1.5 rounded transition-colors">Call Customer</button>
                  </div>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

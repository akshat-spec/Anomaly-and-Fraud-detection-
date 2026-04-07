import React, { useEffect, useState } from "react";
import { Server, CheckCircle2, XCircle, Clock } from "lucide-react";
import { getHealth } from "../api/client";
import type { HealthResponse } from "../types";

export const ModelHealth: React.FC = () => {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [isError, setIsError] = useState(false);

  useEffect(() => {
    const check = async () => {
      try {
        const res = await getHealth();
        setHealth(res);
        setIsError(false);
      } catch (e) {
        setIsError(true);
      }
    };
    check();
    const interval = setInterval(check, 10000);
    return () => clearInterval(interval);
  }, []);

  if (!health && !isError) {
    return <div className="h-[140px] w-full bg-[#111111] animate-pulse rounded-xl" />;
  }

  const isHealthy = !isError && health?.status === "healthy" && health?.redis_status === "ok";

  return (
    <div className="flex flex-col bg-[#111111] border border-gray-800 rounded-xl p-5 shadow-lg h-full">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-gray-100 font-semibold tracking-tight">System Status</h2>
        {isHealthy ? (
          <span className="flex items-center gap-1.5 px-2.5 py-1 bg-emerald-500/10 text-emerald-400 text-xs font-semibold rounded-md border border-emerald-500/20">
            <CheckCircle2 size={14} /> ONLINE
          </span>
        ) : (
          <span className="flex items-center gap-1.5 px-2.5 py-1 bg-red-500/10 text-red-400 text-xs font-semibold rounded-md border border-red-500/20">
            <XCircle size={14} /> DEGRADED
          </span>
        )}
      </div>

      <div className="space-y-4 flex-1">
        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-500 flex items-center gap-2">
            <Server size={14} /> Ensemble Engine
          </span>
          <span className="text-gray-200 font-mono text-xs">{health?.model_version || "unknown"}</span>
        </div>

        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-500 flex items-center gap-2">
            <Clock size={14} /> Uptime
          </span>
          <span className="text-gray-200 font-mono text-xs">
            {health?.uptime_seconds ? `${(health.uptime_seconds / 3600).toFixed(1)} hrs` : "--"}
          </span>
        </div>

        <div className="flex flex-col mt-4 pt-4 border-t border-gray-800">
          <div className="flex items-center justify-between text-xs mb-2">
            <span className="text-gray-400 font-medium">Model Efficacy (Validation)</span>
          </div>
          <div className="grid grid-cols-2 gap-2 text-center text-xs">
            <div className="bg-gray-900 border border-gray-800 rounded p-2 shadow-inner">
              <div className="text-gray-500 mb-1">PR-AUC</div>
              <div className="text-emerald-400 font-bold text-sm">0.998</div>
            </div>
            <div className="bg-gray-900 border border-gray-800 rounded p-2 shadow-inner">
              <div className="text-gray-500 mb-1">F1 Score</div>
              <div className="text-emerald-400 font-bold text-sm">0.854</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

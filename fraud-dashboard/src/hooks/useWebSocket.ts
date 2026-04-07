import { useEffect, useRef, useState, useCallback } from "react";
import type { TransactionEvent } from "../types";

const WS_URL = import.meta.env.VITE_WS_URL || "ws://localhost:8000/ws/transactions";

export const useWebSocket = () => {
  const [messages, setMessages] = useState<TransactionEvent[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const ws = useRef<WebSocket | null>(null);
  const reconnectTimeout = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Use a ref to always read the latest paused state inside handlers
  const isPausedRef = useRef(isPaused);
  useEffect(() => {
    isPausedRef.current = isPaused;
  }, [isPaused]);

  const connect = useCallback(() => {
    try {
      ws.current = new WebSocket(WS_URL);

      ws.current.onopen = () => {
        setIsConnected(true);
        console.log("WS Connected", WS_URL);
        if (reconnectTimeout.current) clearTimeout(reconnectTimeout.current);
      };

      ws.current.onmessage = (event) => {
        if (isPausedRef.current) return;
        try {
          const newTxn: TransactionEvent = JSON.parse(event.data);
          setMessages((prev) => {
            const updated = [newTxn, ...prev];
            // Keep the last 500 records only for memory efficiency
            if (updated.length > 500) updated.pop();
            return updated;
          });
        } catch (e) {
          console.error("WS Parse error", e);
        }
      };

      ws.current.onclose = () => {
        setIsConnected(false);
        console.log("WS Disconnected. Reconnecting in 3s...");
        reconnectTimeout.current = setTimeout(connect, 3000);
      };

      ws.current.onerror = (err) => {
        console.error("WS Error:", err);
        ws.current?.close();
      };
    } catch (e) {
      console.error("WS Connection error:", e);
      reconnectTimeout.current = setTimeout(connect, 3000);
    }
  }, []);

  useEffect(() => {
    connect();
    return () => {
      if (reconnectTimeout.current) clearTimeout(reconnectTimeout.current);
      ws.current?.close();
    };
  }, [connect]);

  const togglePause = () => setIsPaused(!isPaused);

  return { messages, isConnected, isPaused, togglePause };
};

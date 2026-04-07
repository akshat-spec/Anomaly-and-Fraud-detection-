export interface TransactionRequest {
  transaction_id: string;
  user_id: string;
  timestamp: string; // ISO8601
  amount: number;
  v1?: number;
  [key: string]: string | number | undefined; // optional V params
}

export interface FraudResponse {
  transaction_id: string;
  fraud: boolean;
  xgb_score: number;
  iso_score: number;
  confidence: number;
  latency_ms: number;
  cached: boolean;
}

export interface MetricCardData {
  total_transactions: number;
  fraud_detected: number;
  false_positive_rate: number;
  avg_latency_p99: number;
}

export interface HealthResponse {
  status: string;
  uptime_seconds: number;
  model_version: string;
  redis_status: string;
}

export interface AlertSchema {
  id: string;
  transaction_id: string;
  user_id: string;
  is_fraud: boolean;
  xgb_score: number;
  iso_score: number;
  confidence: number;
  created_at: string;
  reviewed: boolean;
}

// Websocket Events Streaming schema mirroring the pipeline enrichment output
export interface TransactionEvent {
  transaction_id: string;
  user_id: string;
  timestamp: number | string;
  amount: number;
  fraud: boolean;
  xgb_score: number;
  iso_score: number;
  confidence: number;
  latency_ms: number;
}

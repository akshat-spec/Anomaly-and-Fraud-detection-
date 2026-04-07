import axios from "axios";
import type { HealthResponse, MetricCardData, AlertSchema } from "../types";

export const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

const apiClient = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  headers: {
    "Content-type": "application/json",
  },
});

export const getHealth = async (): Promise<HealthResponse> => {
  // Health is usually at the root, not inside /api/v1/
  const response = await axios.get<HealthResponse>(`${API_BASE_URL}/health`);
  return response.data;
};

// Assuming the metrics/stats APIs exist on backend (as requested in the prompt)
export const getStats = async (): Promise<MetricCardData> => {
  const response = await apiClient.get<MetricCardData>("/stats");
  return response.data;
};

export const getAlerts = async (): Promise<AlertSchema[]> => {
  const response = await apiClient.get<AlertSchema[]>("/alerts");
  return response.data;
};

export const markAlertReviewed = async (id: string): Promise<AlertSchema> => {
  const response = await apiClient.patch<AlertSchema>(`/alerts/${id}/review`);
  return response.data;
};

export default apiClient;

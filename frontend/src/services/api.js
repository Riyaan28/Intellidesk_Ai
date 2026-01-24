/**
 * API Service
 * Handles all API calls to backend
 */

import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Email Processing
export const processEmail = async (emailData) => {
  const response = await api.post("/api/emails/process", emailData);
  return response.data;
};

export const batchProcessEmails = async (emails) => {
  const response = await api.post("/api/emails/batch-process", emails);
  return response.data;
};

// Tickets
export const getTickets = async (params = {}) => {
  const response = await api.get("/api/tickets/", { params });
  return response.data;
};

export const getTicket = async (ticketId) => {
  const response = await api.get(`/api/tickets/${ticketId}`);
  return response.data;
};

export const updateTicketStatus = async (
  ticketId,
  status,
  resolution = null,
) => {
  const response = await api.patch(`/api/tickets/${ticketId}/status`, {
    status,
    resolution,
  });
  return response.data;
};

export const addTicketNote = async (ticketId, note) => {
  const response = await api.post(`/api/tickets/${ticketId}/notes`, { note });
  return response.data;
};

export const getTicketThread = async (ticketId) => {
  const response = await api.get(`/api/tickets/${ticketId}/thread`);
  return response.data;
};

// Analytics
export const getDashboardStats = async () => {
  const response = await api.get("/api/analytics/dashboard");
  return response.data;
};

export const getTrends = async (days = 30) => {
  const response = await api.get("/api/analytics/trends", { params: { days } });
  return response.data;
};

export const getPerformanceMetrics = async () => {
  const response = await api.get("/api/analytics/performance");
  return response.data;
};

// System
export const healthCheck = async () => {
  const response = await api.get("/health");
  return response.data;
};

export default api;

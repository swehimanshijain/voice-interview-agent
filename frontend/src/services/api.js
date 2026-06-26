import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000/api";

export const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 90000,
});

export async function fetchInterviewTypes() {
  const response = await api.get("/interview-types");
  return response.data;
}

export async function createSession(interviewType) {
  const response = await api.post("/sessions", { interview_type: interviewType });
  return response.data;
}

export async function submitAnswer(sessionId, transcript) {
  const response = await api.post(`/sessions/${sessionId}/answers`, { transcript });
  return response.data;
}

export async function completeSession(sessionId) {
  const response = await api.post(`/sessions/${sessionId}/complete`);
  return response.data;
}

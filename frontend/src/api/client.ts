import type { AgentInstruction, SessionRecord } from "@/types";

const BASE = "/api";

// ── Response envelopes (mirrors backend common/models.py) ──────────────────

export interface DataResponse<T> {
  success: boolean;
  message?: string;
  data?: T;
}

export interface ListResponse<T> {
  success: boolean;
  message?: string;
  data: T[];
  total: number;
}

export interface StatusResponse {
  success: boolean;
  message?: string;
  status?: string;
}

// ── HTTP helper ────────────────────────────────────────────────────────────

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`${res.status}: ${text}`);
  }
  if (res.status === 204) return undefined as T;
  return res.json() as Promise<T>;
}

// ── API calls ──────────────────────────────────────────────────────────────

export const api = {
  listSessions: () =>
    request<ListResponse<SessionRecord>>("/sessions"),

  createSession: (body: {
    request: string;
    project_context?: string;
    review_feedback?: string;
  }) =>
    request<DataResponse<SessionRecord>>("/sessions", {
      method: "POST",
      body: JSON.stringify(body),
    }),

  getSession: (id: string) =>
    request<DataResponse<SessionRecord>>(`/sessions/${id}`),

  getTestSpec: (
    id: string,
    body: { plan: string; scenario?: string; existing_code?: string }
  ) =>
    request<DataResponse<AgentInstruction>>(`/sessions/${id}/test-spec`, {
      method: "POST",
      body: JSON.stringify(body),
    }),

  implement: (
    id: string,
    body: { test_code: string; test_file_path: string; error_output?: string }
  ) =>
    request<DataResponse<AgentInstruction>>(`/sessions/${id}/implement`, {
      method: "POST",
      body: JSON.stringify(body),
    }),

  review: (
    id: string,
    body: { diff: string; changed_files?: string[]; plan?: string }
  ) =>
    request<DataResponse<AgentInstruction>>(`/sessions/${id}/review`, {
      method: "POST",
      body: JSON.stringify(body),
    }),

  fetchContext: (id: string, body: { query: string; limit?: number }) =>
    request<DataResponse<AgentInstruction>>(`/sessions/${id}/context`, {
      method: "POST",
      body: JSON.stringify(body),
    }),

  abandonSession: (id: string) =>
    request<StatusResponse>(`/sessions/${id}`, { method: "DELETE" }),
};

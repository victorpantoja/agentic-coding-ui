import type { SessionDetail, SessionSummary } from "@/types";

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
  return res.json() as Promise<T>;
}

// ── API calls ──────────────────────────────────────────────────────────────

export interface ListSessionsParams {
  search?: string;
  date_from?: string;
  date_to?: string;
  page?: number;
  page_size?: number;
}

export const api = {
  listSessions: (params?: ListSessionsParams) => {
    const qs = new URLSearchParams();
    if (params?.search) qs.set("search", params.search);
    if (params?.date_from) qs.set("date_from", params.date_from);
    if (params?.date_to) qs.set("date_to", params.date_to);
    if (params?.page != null) qs.set("page", String(params.page));
    if (params?.page_size != null) qs.set("page_size", String(params.page_size));
    const query = qs.toString() ? `?${qs}` : "";
    return request<ListResponse<SessionSummary>>(`/sessions${query}`);
  },

  getSession: (id: string) =>
    request<DataResponse<SessionDetail>>(`/sessions/${id}`),
};

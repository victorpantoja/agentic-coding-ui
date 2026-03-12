export interface SessionSummary {
  id: string;
  request: string;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface ContextEvent {
  id: string;
  event_type: string;
  data: Record<string, unknown>;
  summary: string;
  created_at: string;
}

export interface SessionDetail {
  id: string;
  request: string;
  status: string;
  plan: Record<string, unknown> | null;
  test_spec: Record<string, unknown> | null;
  implementation: Record<string, unknown> | null;
  review: Record<string, unknown> | null;
  created_at: string;
  updated_at: string;
  context: ContextEvent[];
}

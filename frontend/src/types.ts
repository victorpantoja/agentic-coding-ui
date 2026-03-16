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
  agent: string | null;
  duration_ms: number | null;
  created_at: string;
}

export interface TaskHistoryEntry {
  iteration: number;
  reviewer_critique: string;
  diff: string;
  lint_output: Record<string, unknown>;
  arch_output: Record<string, unknown>;
  is_approved: boolean;
  lessons_learned: string;
  created_at: string;
}

export interface SessionStep {
  id: string;
  step_name: string;
  status: "pending" | "running" | "finished" | "failed";
  scheduled_at: string;
  started_at: string | null;
  ended_at: string | null;
  error_details: string | null;
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
  steps: SessionStep[];
  task_history: TaskHistoryEntry[];
}

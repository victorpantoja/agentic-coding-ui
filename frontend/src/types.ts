export type SessionStatus =
  | "active"
  | "testing"
  | "implementing"
  | "reviewing"
  | "approved"
  | "rejected"
  | "abandoned";

export interface AgentInstruction {
  agent: string;
  system_prompt: string;
  user_message: string;
  action_required: string;
  session_id: string;
  step: string;
  context: Record<string, unknown>;
}

export interface SessionRecord {
  session_id: string;
  request: string;
  status: SessionStatus;
  instructions: AgentInstruction[];
  created_at: string;
  updated_at: string;
}

export type WsEventType = "instruction" | "status" | "error";

export interface WsEvent {
  type: WsEventType;
  payload: Record<string, unknown>;
}

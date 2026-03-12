import { useEffect, useRef, useState, useCallback } from "react";
import type { AgentInstruction, SessionRecord, WsEvent } from "@/types";

export interface WsState {
  connected: boolean;
  instructions: AgentInstruction[];
  latestStatus: string | null;
}

export function useSessionWebSocket(
  sessionId: string | null,
  onSessionState?: (s: SessionRecord) => void
): WsState {
  const wsRef = useRef<WebSocket | null>(null);
  const [connected, setConnected] = useState(false);
  const [instructions, setInstructions] = useState<AgentInstruction[]>([]);
  const [latestStatus, setLatestStatus] = useState<string | null>(null);

  const handleMessage = useCallback(
    (evt: MessageEvent<string>) => {
      let data: unknown;
      try {
        data = JSON.parse(evt.data);
      } catch {
        return;
      }

      // Initial session state dump (has session_id key)
      if (
        data !== null &&
        typeof data === "object" &&
        "session_id" in data
      ) {
        const session = data as SessionRecord;
        setInstructions(session.instructions);
        setLatestStatus(session.status);
        onSessionState?.(session);
        return;
      }

      // WsEvent
      const event = data as WsEvent;
      if (event.type === "instruction") {
        setInstructions((prev) => [
          ...prev,
          event.payload as unknown as AgentInstruction,
        ]);
      } else if (event.type === "status") {
        const s = event.payload as { status: string };
        setLatestStatus(s.status);
      }
    },
    [onSessionState]
  );

  useEffect(() => {
    if (!sessionId) return;

    const protocol = window.location.protocol === "https:" ? "wss" : "ws";
    const ws = new WebSocket(
      `${protocol}://${window.location.host}/ws/${sessionId}`
    );
    wsRef.current = ws;

    ws.onopen = () => setConnected(true);
    ws.onclose = () => setConnected(false);
    ws.onerror = () => setConnected(false);
    ws.onmessage = handleMessage;

    return () => {
      ws.close();
      setConnected(false);
    };
  }, [sessionId, handleMessage]);

  return { connected, instructions, latestStatus };
}

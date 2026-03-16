import { useEffect, useRef, useState } from "react";
import type { ContextEvent, SessionDetail, SessionStep, TaskHistoryEntry } from "@/types";

const RECONNECT_DELAY_MS = 2000;

export interface WsState {
  connected: boolean;
  detail: SessionDetail | null;
  error: string | null;
}

export function useSessionWebSocket(sessionId: string | null): WsState {
  const [connected, setConnected] = useState(false);
  const [detail, setDetail] = useState<SessionDetail | null>(null);
  const [error, setError] = useState<string | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const retryRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const activeRef = useRef(true);

  useEffect(() => {
    setDetail(null);
    setError(null);
    setConnected(false);
    activeRef.current = true;

    if (!sessionId) return;

    const protocol = window.location.protocol === "https:" ? "wss" : "ws";

    function connect() {
      if (!activeRef.current) return;

      const ws = new WebSocket(`${protocol}://${window.location.host}/ws/${sessionId}`);
      wsRef.current = ws;

      ws.onopen = () => {
        if (!activeRef.current) { ws.close(); return; }
        setConnected(true);
        setError(null);
      };

      ws.onclose = () => {
        setConnected(false);
        if (activeRef.current) {
          retryRef.current = setTimeout(connect, RECONNECT_DELAY_MS);
        }
      };

      ws.onerror = () => {
        setConnected(false);
        ws.close();
      };

      ws.onmessage = (evt: MessageEvent<string>) => {
        const msg: { type: string; data: unknown } = JSON.parse(evt.data);
        if (msg.type === "session") {
          setDetail(msg.data as SessionDetail);
        } else if (msg.type === "context_event") {
          setDetail((prev) =>
            prev
              ? { ...prev, context: [...prev.context, msg.data as ContextEvent] }
              : null
          );
        } else if (msg.type === "steps") {
          setDetail((prev) =>
            prev ? { ...prev, steps: msg.data as SessionStep[] } : null
          );
        } else if (msg.type === "task_history") {
          setDetail((prev) =>
            prev ? { ...prev, task_history: msg.data as TaskHistoryEntry[] } : null
          );
        } else if (msg.type === "status") {
          setDetail((prev) =>
            prev ? { ...prev, ...(msg.data as Partial<SessionDetail>) } : null
          );
        } else if (msg.type === "error") {
          setError((msg.data as { detail: string }).detail);
        }
      };
    }

    connect();

    return () => {
      activeRef.current = false;
      if (retryRef.current) clearTimeout(retryRef.current);
      wsRef.current?.close();
    };
  }, [sessionId]);

  return { connected, detail, error };
}

import { useEffect, useRef, useState } from "react";
import type { ContextEvent, SessionDetail } from "@/types";

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

  useEffect(() => {
    setDetail(null);
    setError(null);
    setConnected(false);

    if (!sessionId) return;

    const protocol = window.location.protocol === "https:" ? "wss" : "ws";
    const ws = new WebSocket(`${protocol}://${window.location.host}/ws/${sessionId}`);
    wsRef.current = ws;

    ws.onopen = () => setConnected(true);
    ws.onclose = () => setConnected(false);
    ws.onerror = () => {
      setConnected(false);
      setError("WebSocket connection failed");
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
      } else if (msg.type === "status") {
        setDetail((prev) =>
          prev ? { ...prev, ...(msg.data as Partial<SessionDetail>) } : null
        );
      } else if (msg.type === "error") {
        setError((msg.data as { detail: string }).detail);
      }
    };

    return () => {
      ws.close();
    };
  }, [sessionId]);

  return { connected, detail, error };
}

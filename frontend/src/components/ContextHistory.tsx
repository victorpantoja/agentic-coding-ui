import { Brain, Zap, CheckCircle, Search, MessageSquare } from "lucide-react";
import type { ContextEvent } from "@/types";
import { Badge } from "@/components/ui/badge";

export const EVENT_ICONS: Record<string, React.ReactNode> = {
  plan: <Brain className="h-4 w-4" />,
  test: <Zap className="h-4 w-4" />,
  implement: <CheckCircle className="h-4 w-4" />,
  review: <Search className="h-4 w-4" />,
  feedback: <MessageSquare className="h-4 w-4" />,
};

export const EVENT_COLORS: Record<string, string> = {
  plan: "text-violet-500",
  test: "text-yellow-500",
  implement: "text-green-500",
  review: "text-blue-500",
  feedback: "text-orange-500",
};

function EventBlock({ event }: { event: ContextEvent }) {
  const color = EVENT_COLORS[event.event_type] ?? "text-muted-foreground";
  const icon = EVENT_ICONS[event.event_type] ?? <Brain className="h-4 w-4" />;
  const ts = new Date(event.created_at).toLocaleString();

  return (
    <div className="border-l-2 border-border/50 pl-4 pb-6 last:pb-0">
      <div className="flex items-center gap-2 mb-1">
        <span className={color}>{icon}</span>
        <span className={`text-sm font-semibold capitalize ${color}`}>{event.event_type}</span>
        <Badge className="text-[10px] px-1.5 py-0 bg-muted text-muted-foreground border-0">
          {ts}
        </Badge>
      </div>
      {event.summary && (
        <p className="text-sm text-foreground/80 mb-2">{event.summary}</p>
      )}
      {Object.keys(event.data).length > 0 && (
        <details>
          <summary className="cursor-pointer text-xs text-muted-foreground hover:text-foreground transition-colors select-none">
            Data ↓
          </summary>
          <pre className="mt-2 whitespace-pre-wrap font-mono text-xs bg-muted/30 border border-border/50 rounded p-3 leading-relaxed overflow-x-auto">
            {JSON.stringify(event.data, null, 2)}
          </pre>
        </details>
      )}
    </div>
  );
}

interface Props {
  events: ContextEvent[];
}

export function ContextHistory({ events }: Props) {
  if (events.length === 0) return null;
  return (
    <div className="p-4 space-y-0">
      {events.map((event) => (
        <EventBlock key={event.id} event={event} />
      ))}
    </div>
  );
}

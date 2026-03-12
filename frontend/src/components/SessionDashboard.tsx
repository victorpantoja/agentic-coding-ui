import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  Activity,
  Brain,
  Calendar,
  CheckCircle,
  CheckCircle2,
  ChevronDown,
  Clock,
  Loader2,
  MessageSquare,
  Moon,
  Search,
  Sun,
  Wifi,
  WifiOff,
  XCircle,
  Zap,
} from "lucide-react";
import { api } from "@/api/client";
import { SessionCard } from "@/components/SessionCard";
import { ContextHistory, EVENT_COLORS, EVENT_ICONS } from "@/components/ContextHistory";
import { JsonPanel } from "@/components/JsonPanel";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useSessionWebSocket } from "@/hooks/useWebSocket";
import { cn, formatRelativeDate, statusColor } from "@/lib/utils";
import type { ContextEvent, SessionDetail, SessionStep } from "@/types";

const PAGE_SIZE = 20;
const ACTIVE_STATUSES = new Set(["active", "testing", "implementing", "reviewing"]);

interface Section {
  key: string;
  title: string;
  eventType: string;
  stepName: string | null;
  jsonField: keyof SessionDetail | null;
  icon: React.ReactNode;
  color: string;
}

const SECTIONS: Section[] = [
  {
    key: "plan",
    title: "Plan",
    eventType: "plan",
    stepName: "plan",
    jsonField: "plan",
    icon: EVENT_ICONS.plan ?? <Brain className="h-4 w-4" />,
    color: EVENT_COLORS.plan,
  },
  {
    key: "tests",
    title: "Tests",
    eventType: "test",
    stepName: "test",
    jsonField: "test_spec",
    icon: EVENT_ICONS.test ?? <Zap className="h-4 w-4" />,
    color: EVENT_COLORS.test,
  },
  {
    key: "implementation",
    title: "Implementation",
    eventType: "implement",
    stepName: "implement",
    jsonField: "implementation",
    icon: EVENT_ICONS.implement ?? <CheckCircle className="h-4 w-4" />,
    color: EVENT_COLORS.implement,
  },
  {
    key: "review",
    title: "Review",
    eventType: "review",
    stepName: "review",
    jsonField: "review",
    icon: EVENT_ICONS.review ?? <Search className="h-4 w-4" />,
    color: EVENT_COLORS.review,
  },
  {
    key: "feedback",
    title: "Feedback",
    eventType: "feedback",
    stepName: null,
    jsonField: null,
    icon: EVENT_ICONS.feedback ?? <MessageSquare className="h-4 w-4" />,
    color: EVENT_COLORS.feedback,
  },
];

function StepStatusIcon({ status }: { status: SessionStep["status"] }) {
  if (status === "finished")
    return <CheckCircle2 className="h-4 w-4 text-green-500 shrink-0" />;
  if (status === "running")
    return <Loader2 className="h-4 w-4 text-blue-500 animate-spin shrink-0" />;
  if (status === "failed")
    return <XCircle className="h-4 w-4 text-destructive shrink-0" />;
  return <Clock className="h-4 w-4 text-muted-foreground shrink-0" />;
}

interface CollapsibleProps {
  title: string;
  icon: React.ReactNode;
  color: string;
  children: React.ReactNode;
  defaultOpen?: boolean;
  badge?: string;
  step?: SessionStep;
}

function CollapsibleSection({
  title,
  icon,
  color,
  children,
  defaultOpen = true,
  badge,
  step,
}: CollapsibleProps) {
  const [open, setOpen] = useState(defaultOpen);
  return (
    <div className="border border-border rounded-lg overflow-hidden">
      <button
        onClick={() => setOpen((o) => !o)}
        className="w-full flex items-center gap-3 px-4 py-2.5 bg-muted/30 hover:bg-muted/50 transition-colors text-sm font-medium text-left"
      >
        <span className={cn("shrink-0", color)}>{icon}</span>
        <span className="flex-1">{title}</span>
        {badge && (
          <span className="text-[10px] bg-muted text-muted-foreground rounded px-1.5 py-0.5">
            {badge}
          </span>
        )}
        {step && <StepStatusIcon status={step.status} />}
        <ChevronDown
          className={cn(
            "h-4 w-4 text-muted-foreground transition-transform shrink-0",
            open && "rotate-180"
          )}
        />
      </button>
      {open && <div className="border-t border-border">{children}</div>}
    </div>
  );
}

function SessionDetailPanel({
  detail,
  connected,
}: {
  detail: SessionDetail;
  connected: boolean;
}) {
  const isLive = ACTIVE_STATUSES.has(detail.status);

  const eventsByType = detail.context.reduce<Record<string, ContextEvent[]>>((acc, e) => {
    (acc[e.event_type] ??= []).push(e);
    return acc;
  }, {});

  const stepByName = Object.fromEntries(detail.steps.map((s) => [s.step_name, s]));

  const visibleSections = SECTIONS.filter((s) => {
    const hasEvents = (eventsByType[s.eventType]?.length ?? 0) > 0;
    const hasJson = s.jsonField != null && detail[s.jsonField] != null;
    const hasStep = s.stepName != null && stepByName[s.stepName] != null;
    return hasEvents || hasJson || hasStep;
  });

  return (
    <div className="flex-1 flex flex-col min-h-0">
      {/* Header */}
      <header className="px-6 py-4 border-b border-border shrink-0">
        <div className="flex items-start justify-between gap-4">
          <div className="min-w-0">
            <h2 className="font-semibold text-base leading-snug mb-1">{detail.request}</h2>
            <p className="font-mono text-[11px] text-muted-foreground">{detail.id}</p>
          </div>
          <div className="shrink-0 flex flex-col items-end gap-1.5 text-xs text-muted-foreground">
            <div className="flex items-center gap-2">
              <Badge className={cn("text-[10px] px-1.5 py-0", statusColor(detail.status))}>
                {detail.status}
              </Badge>
              {isLive && connected ? (
                <span className="flex items-center gap-1 text-green-600 dark:text-green-400">
                  <Wifi className="h-3 w-3" />
                  <span className="text-[10px]">Live</span>
                </span>
              ) : isLive && !connected ? (
                <span className="flex items-center gap-1 text-muted-foreground">
                  <WifiOff className="h-3 w-3" />
                  <span className="text-[10px]">Reconnecting…</span>
                </span>
              ) : null}
            </div>
            <span>Updated {formatRelativeDate(detail.updated_at)}</span>
            <span>Created {formatRelativeDate(detail.created_at)}</span>
          </div>
        </div>
      </header>

      {/* Sections */}
      <ScrollArea className="flex-1">
        <div className="p-6 space-y-3">
          {visibleSections.length === 0 && (
            <p className="text-sm text-muted-foreground text-center py-8">No activity yet.</p>
          )}
          {visibleSections.map((section) => {
            const events = eventsByType[section.eventType] ?? [];
            const jsonData =
              section.jsonField != null
                ? (detail[section.jsonField] as Record<string, unknown> | null)
                : null;
            const badge = events.length > 0 ? String(events.length) : undefined;

            const step = section.stepName ? stepByName[section.stepName] : undefined;

            return (
              <CollapsibleSection
                key={section.key}
                title={section.title}
                icon={section.icon}
                color={section.color}
                badge={badge}
                step={step}
                defaultOpen
              >
                <ContextHistory events={events} />
                {events.length > 0 && jsonData && (
                  <div className="mx-4 border-t border-border/50 mb-3" />
                )}
                {jsonData && (
                  <JsonPanel label={section.title.toLowerCase()} data={jsonData} />
                )}
              </CollapsibleSection>
            );
          })}
        </div>
      </ScrollArea>
    </div>
  );
}

interface Props {
  darkMode: boolean;
  onToggleDark: () => void;
}

export function SessionDashboard({ darkMode, onToggleDark }: Props) {
  const [activeId, setActiveId] = useState<string | null>(null);
  const [search, setSearch] = useState("");
  const [dateFrom, setDateFrom] = useState("");
  const [dateTo, setDateTo] = useState("");
  const [page, setPage] = useState(1);

  const { data: sessionsResp, isLoading } = useQuery({
    queryKey: ["sessions", search, dateFrom, dateTo, page],
    queryFn: () =>
      api.listSessions({
        search: search || undefined,
        date_from: dateFrom || undefined,
        date_to: dateTo || undefined,
        page,
        page_size: PAGE_SIZE,
      }),
    refetchInterval: 10_000,
  });

  const sessions = sessionsResp?.data ?? [];
  const total = sessionsResp?.total ?? 0;
  const pageCount = Math.max(1, Math.ceil(total / PAGE_SIZE));

  const { connected, detail, error } = useSessionWebSocket(activeId);

  const handleSearch = (v: string) => { setSearch(v); setPage(1); };
  const handleDateFrom = (v: string) => { setDateFrom(v); setPage(1); };
  const handleDateTo = (v: string) => { setDateTo(v); setPage(1); };

  return (
    <div className="flex h-screen bg-background text-foreground overflow-hidden">
      {/* Sidebar */}
      <aside className="w-96 shrink-0 border-r border-border flex flex-col">
        <div className="px-4 py-3 border-b border-border flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <Activity className="h-5 w-5 text-primary shrink-0" />
            <div>
              <h1 className="font-semibold text-base leading-tight">Agentic Dashboard</h1>
              <p className="text-xs text-muted-foreground">sovereign-brain sessions</p>
            </div>
          </div>
          <Button
            variant="ghost"
            size="icon"
            onClick={onToggleDark}
            className="h-8 w-8 shrink-0"
            title={darkMode ? "Switch to light mode" : "Switch to dark mode"}
          >
            {darkMode ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
          </Button>
        </div>

        <div className="px-4 py-3 border-b border-border space-y-2">
          <div className="relative">
            <Search className="absolute left-2.5 top-2.5 h-3.5 w-3.5 text-muted-foreground pointer-events-none" />
            <Input
              placeholder="Search by request…"
              value={search}
              onChange={(e) => handleSearch(e.target.value)}
              className="pl-8 h-8 text-sm"
            />
          </div>
          <div className="flex gap-2 items-center">
            <Calendar className="h-3.5 w-3.5 text-muted-foreground shrink-0" />
            <Input
              type="date"
              value={dateFrom}
              onChange={(e) => handleDateFrom(e.target.value)}
              className="h-7 text-xs flex-1"
              title="Updated from"
            />
            <span className="text-xs text-muted-foreground">–</span>
            <Input
              type="date"
              value={dateTo}
              onChange={(e) => handleDateTo(e.target.value)}
              className="h-7 text-xs flex-1"
              title="Updated to"
            />
          </div>
          <p className="text-xs text-muted-foreground">
            {total} session{total !== 1 ? "s" : ""}
            {search || dateFrom || dateTo ? " (filtered)" : ""}
          </p>
        </div>

        <ScrollArea className="flex-1">
          <div className="p-3 space-y-2">
            {isLoading && (
              <p className="text-sm text-muted-foreground text-center py-8">Loading…</p>
            )}
            {!isLoading && sessions.length === 0 && (
              <p className="text-sm text-muted-foreground text-center py-8">No sessions found.</p>
            )}
            {sessions.map((session) => (
              <SessionCard
                key={session.id}
                session={session}
                active={session.id === activeId}
                onClick={() => setActiveId(session.id)}
              />
            ))}
          </div>
        </ScrollArea>

        {pageCount > 1 && (
          <div className="px-4 py-3 border-t border-border flex items-center justify-between">
            <Button
              variant="outline"
              size="sm"
              disabled={page <= 1}
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              className="h-7 text-xs px-3"
            >
              ← Prev
            </Button>
            <span className="text-xs text-muted-foreground">{page} / {pageCount}</span>
            <Button
              variant="outline"
              size="sm"
              disabled={page >= pageCount}
              onClick={() => setPage((p) => Math.min(pageCount, p + 1))}
              className="h-7 text-xs px-3"
            >
              Next →
            </Button>
          </div>
        )}
      </aside>

      {/* Main panel */}
      <main className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {!activeId ? (
          <div className="flex-1 flex flex-col items-center justify-center text-muted-foreground">
            <Activity className="h-12 w-12 opacity-20 mb-4" />
            <p className="text-lg font-medium opacity-50">Select a session to view</p>
          </div>
        ) : error ? (
          <div className="flex-1 flex flex-col items-center justify-center">
            <p className="text-sm text-destructive">{error}</p>
          </div>
        ) : !detail ? (
          <div className="flex-1 flex flex-col items-center justify-center text-muted-foreground">
            <p className="text-sm">Connecting…</p>
          </div>
        ) : (
          <SessionDetailPanel detail={detail} connected={connected} />
        )}
      </main>
    </div>
  );
}

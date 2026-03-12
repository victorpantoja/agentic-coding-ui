import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Activity, Calendar, Moon, Search, Sun } from "lucide-react";
import { api } from "@/api/client";
import { SessionCard } from "@/components/SessionCard";
import { ContextHistory } from "@/components/ContextHistory";
import { JsonPanel } from "@/components/JsonPanel";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { cn, formatRelativeDate, statusColor } from "@/lib/utils";

const PAGE_SIZE = 20;

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

  // Debounce search: commit on Enter or blur, or just use live search
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

  const { data: sessionResp, isLoading: isLoadingDetail } = useQuery({
    queryKey: ["session", activeId],
    queryFn: () => api.getSession(activeId!),
    enabled: activeId != null,
  });

  const detail = sessionResp?.data;

  const handleSearch = (v: string) => {
    setSearch(v);
    setPage(1);
  };
  const handleDateFrom = (v: string) => {
    setDateFrom(v);
    setPage(1);
  };
  const handleDateTo = (v: string) => {
    setDateTo(v);
    setPage(1);
  };

  return (
    <div className="flex h-screen bg-background text-foreground overflow-hidden">
      {/* Sidebar */}
      <aside className="w-96 shrink-0 border-r border-border flex flex-col">
        {/* Header */}
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

        {/* Filters */}
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

        {/* Session list */}
        <ScrollArea className="flex-1">
          <div className="p-3 space-y-2">
            {isLoading && (
              <p className="text-sm text-muted-foreground text-center py-8">Loading…</p>
            )}
            {!isLoading && sessions.length === 0 && (
              <p className="text-sm text-muted-foreground text-center py-8">
                {total === 0 ? "No sessions found." : "No sessions match your filters."}
              </p>
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

        {/* Pagination */}
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
            <span className="text-xs text-muted-foreground">
              {page} / {pageCount}
            </span>
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
      <main className="flex-1 flex flex-col min-w-0">
        {activeId ? (
          <>
            <header className="px-6 py-4 border-b border-border shrink-0">
              {isLoadingDetail ? (
                <p className="text-sm text-muted-foreground">Loading…</p>
              ) : detail ? (
                <div className="flex items-start justify-between gap-4">
                  <div className="min-w-0">
                    <h2 className="font-semibold text-base leading-snug mb-1">{detail.request}</h2>
                    <p className="font-mono text-[11px] text-muted-foreground">{detail.id}</p>
                  </div>
                  <div className="shrink-0 flex flex-col items-end gap-1 text-xs text-muted-foreground">
                    <Badge className={cn("text-[10px] px-1.5 py-0", statusColor(detail.status))}>
                      {detail.status}
                    </Badge>
                    <span>Updated {formatRelativeDate(detail.updated_at)}</span>
                    <span>Created {formatRelativeDate(detail.created_at)}</span>
                  </div>
                </div>
              ) : null}
            </header>

            {detail && (
              <Tabs defaultValue="context" className="flex-1 flex flex-col min-h-0">
                <TabsList className="mx-6 mt-4 w-fit">
                  <TabsTrigger value="context">
                    Context ({detail.context.length})
                  </TabsTrigger>
                  <TabsTrigger value="plan" disabled={!detail.plan}>Plan</TabsTrigger>
                  <TabsTrigger value="tests" disabled={!detail.test_spec}>Tests</TabsTrigger>
                  <TabsTrigger value="implementation" disabled={!detail.implementation}>
                    Implementation
                  </TabsTrigger>
                  <TabsTrigger value="review" disabled={!detail.review}>Review</TabsTrigger>
                </TabsList>

                <TabsContent value="context" className="flex-1 min-h-0 mx-6 mb-6">
                  <div className="h-full rounded-lg border border-border overflow-hidden">
                    <ContextHistory events={detail.context} />
                  </div>
                </TabsContent>

                <TabsContent value="plan" className="flex-1 min-h-0 mx-6 mb-6">
                  <div className="h-full rounded-lg border border-border overflow-hidden">
                    <JsonPanel label="plan" data={detail.plan} />
                  </div>
                </TabsContent>

                <TabsContent value="tests" className="flex-1 min-h-0 mx-6 mb-6">
                  <div className="h-full rounded-lg border border-border overflow-hidden">
                    <JsonPanel label="test spec" data={detail.test_spec} />
                  </div>
                </TabsContent>

                <TabsContent value="implementation" className="flex-1 min-h-0 mx-6 mb-6">
                  <div className="h-full rounded-lg border border-border overflow-hidden">
                    <JsonPanel label="implementation" data={detail.implementation} />
                  </div>
                </TabsContent>

                <TabsContent value="review" className="flex-1 min-h-0 mx-6 mb-6">
                  <div className="h-full rounded-lg border border-border overflow-hidden">
                    <JsonPanel label="review" data={detail.review} />
                  </div>
                </TabsContent>
              </Tabs>
            )}
          </>
        ) : (
          <div className="flex-1 flex flex-col items-center justify-center text-muted-foreground">
            <Activity className="h-12 w-12 opacity-20 mb-4" />
            <p className="text-lg font-medium opacity-50">Select a session to view</p>
          </div>
        )}
      </main>
    </div>
  );
}

import { useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Activity, Calendar, Moon, Search, Sun, Wifi, WifiOff } from "lucide-react";
import { api } from "@/api/client";
import { SessionCard } from "@/components/SessionCard";
import { LiveMonologue } from "@/components/LiveMonologue";
import { DiffViewer } from "@/components/DiffViewer";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { useSessionWebSocket } from "@/hooks/useWebSocket";
import type { SessionRecord } from "@/types";

const PAGE_SIZE = 10;

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
    queryKey: ["sessions"],
    queryFn: api.listSessions,
    refetchInterval: 5000,
  });

  const sessions: SessionRecord[] = useMemo(() => {
    const all = sessionsResp?.data ?? [];
    return [...all].sort(
      (a, b) => new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime()
    );
  }, [sessionsResp]);

  const filtered = useMemo(() => {
    const q = search.toLowerCase();
    return sessions.filter((s) => {
      if (
        q &&
        !s.request.toLowerCase().includes(q) &&
        !s.session_id.toLowerCase().includes(q)
      )
        return false;
      if (dateFrom && new Date(s.updated_at) < new Date(dateFrom)) return false;
      if (dateTo && new Date(s.updated_at) > new Date(dateTo + "T23:59:59Z")) return false;
      return true;
    });
  }, [sessions, search, dateFrom, dateTo]);

  const pageCount = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE));
  const safePage = Math.min(page, pageCount);
  const paged = filtered.slice((safePage - 1) * PAGE_SIZE, safePage * PAGE_SIZE);

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

  const { connected, instructions } = useSessionWebSocket(activeId);
  const activeSession = sessions.find((s) => s.session_id === activeId);
  const mergedInstructions = activeSession
    ? activeSession.instructions.length >= instructions.length
      ? activeSession.instructions
      : instructions
    : instructions;

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
              placeholder="Search by request or ID…"
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
            {filtered.length} session{filtered.length !== 1 ? "s" : ""}
            {search || dateFrom || dateTo ? " (filtered)" : ""}
          </p>
        </div>

        {/* Session list */}
        <ScrollArea className="flex-1">
          <div className="p-3 space-y-2">
            {isLoading && (
              <p className="text-sm text-muted-foreground text-center py-8">Loading…</p>
            )}
            {!isLoading && filtered.length === 0 && (
              <p className="text-sm text-muted-foreground text-center py-8">
                {sessions.length === 0
                  ? "No sessions yet."
                  : "No sessions match your filters."}
              </p>
            )}
            {paged.map((session) => (
              <SessionCard
                key={session.session_id}
                session={session}
                active={session.session_id === activeId}
                onClick={() => setActiveId(session.session_id)}
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
              disabled={safePage <= 1}
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              className="h-7 text-xs px-3"
            >
              ← Prev
            </Button>
            <span className="text-xs text-muted-foreground">
              {safePage} / {pageCount}
            </span>
            <Button
              variant="outline"
              size="sm"
              disabled={safePage >= pageCount}
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
            <header className="px-6 py-4 border-b border-border flex items-center justify-between shrink-0">
              <div className="min-w-0">
                <h2 className="font-semibold truncate max-w-lg text-base">
                  {activeSession?.request ?? activeId}
                </h2>
                <p className="text-xs font-mono text-muted-foreground mt-0.5">{activeId}</p>
              </div>
              <div className="flex items-center gap-1.5 text-xs shrink-0 ml-4">
                {connected ? (
                  <>
                    <Wifi className="h-3.5 w-3.5 text-green-600 dark:text-green-400" />
                    <span className="text-green-600 dark:text-green-400">Live</span>
                  </>
                ) : (
                  <>
                    <WifiOff className="h-3.5 w-3.5 text-muted-foreground" />
                    <span className="text-muted-foreground">Offline</span>
                  </>
                )}
              </div>
            </header>

            <Tabs defaultValue="monologue" className="flex-1 flex flex-col min-h-0">
              <TabsList className="mx-6 mt-4 w-fit">
                <TabsTrigger value="monologue">Live Monologue</TabsTrigger>
                <TabsTrigger value="diff">Diff Viewer</TabsTrigger>
              </TabsList>

              <TabsContent value="monologue" className="flex-1 min-h-0 mx-6 mb-6">
                <div className="h-full rounded-lg border border-border overflow-hidden">
                  <LiveMonologue instructions={mergedInstructions} connected={connected} />
                </div>
              </TabsContent>

              <TabsContent value="diff" className="flex-1 min-h-0 mx-6 mb-6">
                <div className="h-full rounded-lg border border-border overflow-hidden">
                  <DiffViewer instructions={mergedInstructions} />
                </div>
              </TabsContent>
            </Tabs>
          </>
        ) : (
          <div className="flex-1 flex flex-col items-center justify-center text-muted-foreground">
            <Activity className="h-12 w-12 opacity-20 mb-4" />
            <p className="text-lg font-medium opacity-50">Select a session to monitor</p>
          </div>
        )}
      </main>
    </div>
  );
}

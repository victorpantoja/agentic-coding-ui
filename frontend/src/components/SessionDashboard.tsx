import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Activity, Wifi, WifiOff } from "lucide-react";
import { api } from "@/api/client";
import { NewSessionForm } from "@/components/NewSessionForm";
import { SessionCard } from "@/components/SessionCard";
import { LiveMonologue } from "@/components/LiveMonologue";
import { DiffViewer } from "@/components/DiffViewer";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ScrollArea } from "@/components/ui/scroll-area";
import { useSessionWebSocket } from "@/hooks/useWebSocket";
import type { SessionRecord } from "@/types";

export function SessionDashboard() {
  const [activeId, setActiveId] = useState<string | null>(null);

  const { data: sessionsResp, isLoading } = useQuery({
    queryKey: ["sessions"],
    queryFn: api.listSessions,
    refetchInterval: 5000,
  });
  const sessions = sessionsResp?.data ?? [];

  const { connected, instructions } = useSessionWebSocket(activeId);

  const activeSession: SessionRecord | undefined = sessions.find(
    (s) => s.session_id === activeId
  );

  const mergedInstructions = activeSession
    ? activeSession.instructions.length >= instructions.length
      ? activeSession.instructions
      : instructions
    : instructions;

  return (
    <div className="flex h-screen bg-background text-foreground overflow-hidden">
      {/* Sidebar */}
      <aside className="w-80 shrink-0 border-r border-border/50 flex flex-col">
        <div className="p-4 border-b border-border/50">
          <div className="flex items-center gap-2">
            <Activity className="h-5 w-5 text-primary" />
            <h1 className="font-semibold text-lg">Agentic Dashboard</h1>
          </div>
          <p className="text-xs text-muted-foreground mt-1">
            sovereign-brain sessions
          </p>
        </div>

        <div className="p-4 border-b border-border/50">
          <NewSessionForm onCreated={setActiveId} />
        </div>

        <ScrollArea className="flex-1">
          <div className="p-4 space-y-2">
            {isLoading && (
              <p className="text-sm text-muted-foreground text-center py-4">
                Loading…
              </p>
            )}
            {!isLoading && sessions.length === 0 && (
              <p className="text-sm text-muted-foreground text-center py-4">
                No sessions yet.
              </p>
            )}
            {sessions.map((session) => (
              <SessionCard
                key={session.session_id}
                session={session}
                active={session.session_id === activeId}
                onClick={() => setActiveId(session.session_id)}
              />
            ))}
          </div>
        </ScrollArea>
      </aside>

      {/* Main panel */}
      <main className="flex-1 flex flex-col min-w-0">
        {activeId ? (
          <>
            <header className="px-6 py-4 border-b border-border/50 flex items-center justify-between shrink-0">
              <div>
                <h2 className="font-semibold truncate max-w-lg">
                  {activeSession?.request ?? activeId}
                </h2>
                <p className="text-xs font-mono text-muted-foreground mt-0.5">
                  {activeId}
                </p>
              </div>
              <div className="flex items-center gap-1.5 text-xs">
                {connected ? (
                  <>
                    <Wifi className="h-3.5 w-3.5 text-green-400" />
                    <span className="text-green-400">Live</span>
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
                <div className="h-full rounded-lg border border-border/50 overflow-hidden">
                  <LiveMonologue
                    instructions={mergedInstructions}
                    connected={connected}
                  />
                </div>
              </TabsContent>

              <TabsContent value="diff" className="flex-1 min-h-0 mx-6 mb-6">
                <div className="h-full rounded-lg border border-border/50 overflow-hidden">
                  <DiffViewer instructions={mergedInstructions} />
                </div>
              </TabsContent>
            </Tabs>
          </>
        ) : (
          <div className="flex-1 flex flex-col items-center justify-center text-muted-foreground">
            <Activity className="h-12 w-12 opacity-20 mb-4" />
            <p className="text-lg font-medium opacity-50">
              Select a session to monitor
            </p>
            <p className="text-sm opacity-30 mt-1">
              or create a new one in the sidebar
            </p>
          </div>
        )}
      </main>
    </div>
  );
}

import { useMutation, useQueryClient } from "@tanstack/react-query";
import { Trash2 } from "lucide-react";
import type { SessionRecord } from "@/types";
import { api } from "@/api/client";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { cn, statusColor } from "@/lib/utils";

interface Props {
  session: SessionRecord;
  active: boolean;
  onClick: () => void;
}

export function SessionCard({ session, active, onClick }: Props) {
  const queryClient = useQueryClient();

  const abandon = useMutation({
    mutationFn: () => api.abandonSession(session.session_id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["sessions"] }),
  });

  return (
    <Card
      onClick={onClick}
      className={cn(
        "cursor-pointer transition-all hover:border-primary/50",
        active && "border-primary ring-1 ring-primary/30"
      )}
    >
      <CardContent className="p-4">
        <div className="flex items-start justify-between gap-2">
          <div className="min-w-0 flex-1">
            <p className="truncate text-sm font-medium">{session.request}</p>
            <p className="mt-1 font-mono text-xs text-muted-foreground">
              {session.session_id.slice(0, 12)}…
            </p>
          </div>
          <div className="flex items-center gap-2 shrink-0">
            <Badge className={statusColor(session.status)}>
              {session.status}
            </Badge>
            <Button
              variant="ghost"
              size="icon"
              className="h-7 w-7 text-muted-foreground hover:text-destructive"
              onClick={(e) => {
                e.stopPropagation();
                abandon.mutate();
              }}
            >
              <Trash2 className="h-3.5 w-3.5" />
            </Button>
          </div>
        </div>
        <p className="mt-2 text-xs text-muted-foreground">
          {session.instructions.length} instruction
          {session.instructions.length !== 1 ? "s" : ""}
        </p>
      </CardContent>
    </Card>
  );
}

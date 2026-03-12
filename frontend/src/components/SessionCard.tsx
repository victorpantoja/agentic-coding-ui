import { useMutation, useQueryClient } from "@tanstack/react-query";
import { Trash2 } from "lucide-react";
import type { SessionRecord } from "@/types";
import { api } from "@/api/client";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { cn, formatRelativeDate, statusColor } from "@/lib/utils";

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
      <CardContent className="p-3">
        <div className="flex items-start justify-between gap-2 mb-2">
          <p className="truncate text-sm font-medium flex-1 min-w-0">{session.request}</p>
          <Badge className={cn("shrink-0 text-[10px] px-1.5 py-0", statusColor(session.status))}>
            {session.status}
          </Badge>
        </div>

        <p className="font-mono text-[10px] text-muted-foreground truncate mb-2">
          {session.session_id}
        </p>

        <div className="flex items-end justify-between gap-2">
          <div className="text-[11px] text-muted-foreground space-y-0.5 min-w-0">
            <p>Updated {formatRelativeDate(session.updated_at)}</p>
            <p>Created {formatRelativeDate(session.created_at)}</p>
            <p>
              {session.instructions.length} step
              {session.instructions.length !== 1 ? "s" : ""}
            </p>
          </div>
          <Button
            variant="ghost"
            size="icon"
            className="h-6 w-6 text-muted-foreground hover:text-destructive shrink-0"
            onClick={(e) => {
              e.stopPropagation();
              abandon.mutate();
            }}
          >
            <Trash2 className="h-3 w-3" />
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}

import type { SessionSummary } from "@/types";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { cn, formatRelativeDate, statusColor } from "@/lib/utils";

interface Props {
  session: SessionSummary;
  active: boolean;
  onClick: () => void;
}

export function SessionCard({ session, active, onClick }: Props) {
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

        <p className="font-mono text-[10px] text-muted-foreground truncate mb-2">{session.id}</p>

        <div className="text-[11px] text-muted-foreground space-y-0.5">
          <p>Updated {formatRelativeDate(session.updated_at)}</p>
          <p>Created {formatRelativeDate(session.created_at)}</p>
        </div>
      </CardContent>
    </Card>
  );
}

import { ScrollArea } from "@/components/ui/scroll-area";
import { FileCode2 } from "lucide-react";

interface Props {
  label: string;
  data: Record<string, unknown> | null | undefined;
}

export function JsonPanel({ label, data }: Props) {
  if (!data) {
    return (
      <div className="flex flex-col items-center justify-center h-full text-muted-foreground gap-2 py-12">
        <FileCode2 className="h-8 w-8 opacity-30" />
        <p className="text-sm">No {label} data.</p>
      </div>
    );
  }

  return (
    <ScrollArea className="h-full">
      <pre className="p-4 font-mono text-xs leading-relaxed whitespace-pre-wrap break-words">
        {JSON.stringify(data, null, 2)}
      </pre>
    </ScrollArea>
  );
}

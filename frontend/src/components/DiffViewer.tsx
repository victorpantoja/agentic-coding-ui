import { useMemo } from "react";
import { parsePatch } from "diff";
import type { AgentInstruction } from "@/types";
import { ScrollArea } from "@/components/ui/scroll-area";
import { FileCode2 } from "lucide-react";

function extractDiff(instructions: AgentInstruction[]): string {
  // Look for diff content in context or user_message of dev/reviewer steps
  for (const inst of [...instructions].reverse()) {
    if (inst.step === "implement" || inst.step === "review") {
      const ctx = inst.context;
      if (ctx && typeof ctx["diff"] === "string") return ctx["diff"] as string;
      // Try to extract from user_message heuristically
      const match = inst.user_message.match(/```diff\n([\s\S]*?)```/);
      if (match) return match[1];
    }
  }
  return "";
}

interface DiffLineProps {
  line: string;
}

function DiffLine({ line }: DiffLineProps) {
  if (line.startsWith("+") && !line.startsWith("+++")) {
    return (
      <div className="bg-green-950/50 text-green-300 px-4 py-0.5 font-mono text-xs whitespace-pre">
        {line}
      </div>
    );
  }
  if (line.startsWith("-") && !line.startsWith("---")) {
    return (
      <div className="bg-red-950/50 text-red-300 px-4 py-0.5 font-mono text-xs whitespace-pre">
        {line}
      </div>
    );
  }
  if (line.startsWith("@@")) {
    return (
      <div className="bg-blue-950/50 text-blue-400 px-4 py-0.5 font-mono text-xs whitespace-pre">
        {line}
      </div>
    );
  }
  if (line.startsWith("---") || line.startsWith("+++")) {
    return (
      <div className="text-muted-foreground px-4 py-0.5 font-mono text-xs font-semibold whitespace-pre">
        {line}
      </div>
    );
  }
  return (
    <div className="px-4 py-0.5 font-mono text-xs text-foreground/70 whitespace-pre">
      {line}
    </div>
  );
}

interface Props {
  instructions: AgentInstruction[];
}

export function DiffViewer({ instructions }: Props) {
  const rawDiff = useMemo(() => extractDiff(instructions), [instructions]);

  const files = useMemo(() => {
    if (!rawDiff) return [];
    return parsePatch(rawDiff);
  }, [rawDiff]);

  if (!rawDiff || files.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-full text-muted-foreground gap-2 py-12">
        <FileCode2 className="h-8 w-8 opacity-30" />
        <p className="text-sm">No file changes yet.</p>
        <p className="text-xs opacity-60">Diffs appear after implementation.</p>
      </div>
    );
  }

  return (
    <ScrollArea className="h-full">
      <div className="p-4 space-y-4">
        {files.map((file, fi) => (
          <div key={fi} className="rounded-lg border border-border/50 overflow-hidden">
            <div className="bg-muted/40 px-4 py-2 flex items-center gap-2 border-b border-border/50">
              <FileCode2 className="h-4 w-4 text-muted-foreground" />
              <span className="font-mono text-xs font-medium">
                {file.newFileName ?? file.oldFileName ?? "unknown"}
              </span>
            </div>
            <div>
              {file.hunks.map((hunk, hi) => (
                <div key={hi}>
                  <div className="bg-blue-950/50 text-blue-400 px-4 py-0.5 font-mono text-xs">
                    @@ -{hunk.oldStart},{hunk.oldLines} +{hunk.newStart},{hunk.newLines} @@
                  </div>
                  {hunk.lines.map((line, li) => (
                    <DiffLine key={li} line={line} />
                  ))}
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </ScrollArea>
  );
}

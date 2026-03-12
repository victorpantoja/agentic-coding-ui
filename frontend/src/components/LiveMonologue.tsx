import { useEffect, useRef } from "react";
import { Brain, Zap, CheckCircle, Search } from "lucide-react";
import type { AgentInstruction } from "@/types";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Badge } from "@/components/ui/badge";
import { agentColor } from "@/lib/utils";

const AGENT_ICONS: Record<string, React.ReactNode> = {
  architect: <Brain className="h-4 w-4" />,
  tester: <Zap className="h-4 w-4" />,
  dev: <CheckCircle className="h-4 w-4" />,
  reviewer: <Search className="h-4 w-4" />,
};

interface InstructionBlockProps {
  instruction: AgentInstruction;
  index: number;
}

function InstructionBlock({ instruction, index }: InstructionBlockProps) {
  return (
    <div className="border-l-2 border-border/50 pl-4 pb-6 last:pb-0">
      <div className="flex items-center gap-2 mb-2">
        <span className={agentColor(instruction.agent)}>
          {AGENT_ICONS[instruction.agent] ?? <Brain className="h-4 w-4" />}
        </span>
        <span className={`text-sm font-semibold capitalize ${agentColor(instruction.agent)}`}>
          {instruction.agent}
        </span>
        <Badge className="text-[10px] px-1.5 py-0 bg-muted text-muted-foreground border-0">
          step {index + 1} · {instruction.step}
        </Badge>
      </div>

      <div className="space-y-2">
        <div className="rounded-md bg-muted/30 p-3">
          <p className="text-xs text-muted-foreground uppercase tracking-wider mb-1">
            Action Required
          </p>
          <p className="text-sm">{instruction.action_required}</p>
        </div>

        <details className="group">
          <summary className="cursor-pointer text-xs text-muted-foreground hover:text-foreground transition-colors select-none">
            User message ↓
          </summary>
          <pre className="mt-2 whitespace-pre-wrap font-mono text-xs bg-background/50 border border-border/50 rounded p-3 leading-relaxed">
            {instruction.user_message}
          </pre>
        </details>
      </div>
    </div>
  );
}

interface Props {
  instructions: AgentInstruction[];
  connected: boolean;
}

export function LiveMonologue({ instructions, connected }: Props) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [instructions.length]);

  if (instructions.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-full text-muted-foreground gap-2 py-12">
        <Brain className="h-8 w-8 opacity-30" />
        <p className="text-sm">No agent activity yet.</p>
        {connected && (
          <p className="text-xs opacity-60">Listening for instructions…</p>
        )}
      </div>
    );
  }

  return (
    <ScrollArea className="h-full">
      <div className="p-4 space-y-0">
        {instructions.map((inst, i) => (
          <InstructionBlock key={`${inst.session_id}-${i}`} instruction={inst} index={i} />
        ))}
        <div ref={bottomRef} />
      </div>
    </ScrollArea>
  );
}

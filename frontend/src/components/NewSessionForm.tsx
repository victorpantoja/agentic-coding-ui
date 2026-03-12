import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { PlusCircle, Loader2 } from "lucide-react";
import { api } from "@/api/client";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface Props {
  onCreated: (sessionId: string) => void;
}

export function NewSessionForm({ onCreated }: Props) {
  const [request, setRequest] = useState("");
  const queryClient = useQueryClient();

  const mutation = useMutation({
    mutationFn: () => api.createSession({ request }),
    onSuccess: (resp) => {
      queryClient.invalidateQueries({ queryKey: ["sessions"] });
      setRequest("");
      if (resp.data) onCreated(resp.data.session_id);
    },
  });

  return (
    <Card className="border-border/50">
      <CardHeader className="pb-3">
        <CardTitle className="text-sm font-medium text-muted-foreground uppercase tracking-wider">
          New Session
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        <Textarea
          placeholder="Describe what you want to build…"
          value={request}
          onChange={(e) => setRequest(e.target.value)}
          className="min-h-[100px] resize-none bg-background/50"
        />
        <Button
          onClick={() => mutation.mutate()}
          disabled={!request.trim() || mutation.isPending}
          className="w-full"
        >
          {mutation.isPending ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <PlusCircle className="h-4 w-4" />
          )}
          {mutation.isPending ? "Starting…" : "Start Session"}
        </Button>
        {mutation.isError && (
          <p className="text-sm text-destructive">
            {String(mutation.error)}
          </p>
        )}
      </CardContent>
    </Card>
  );
}

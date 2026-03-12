import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { SessionDashboard } from "@/components/SessionDashboard";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 10_000,
      retry: 1,
    },
  },
});

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <SessionDashboard />
    </QueryClientProvider>
  );
}

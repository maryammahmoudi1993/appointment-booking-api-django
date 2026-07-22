import { useState, useEffect, useCallback } from "react";

interface UseApiState<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
}

export function useApi<T>(
  fetcher: () => Promise<{ data: T }>
): UseApiState<T> & { refetch: () => void } {
  const [state, setState] = useState<UseApiState<T>>({
    data: null,
    loading: true,
    error: null,
  });

  const fetchData = useCallback(async () => {
    setState((prev) => ({ ...prev, loading: true, error: null }));
    try {
      const response = await fetcher();
      setState({ data: response.data, loading: false, error: null });
    } catch (err: unknown) {
      const message =
        err instanceof Error ? err.message : "An error occurred";
      setState({ data: null, loading: false, error: message });
    }
  }, [fetcher]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return { ...state, refetch: fetchData };
}

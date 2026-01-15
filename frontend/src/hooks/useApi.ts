import { useState, useEffect, useCallback } from 'react'

interface UseApiState<T> {
  data: T | null
  loading: boolean
  error: Error | null
}

interface UseApiResult<T> extends UseApiState<T> {
  refetch: () => Promise<void>
}

export function useApi<T>(
  fetchFn: () => Promise<T>,
  deps: unknown[] = []
): UseApiResult<T> {
  const [state, setState] = useState<UseApiState<T>>({
    data: null,
    loading: true,
    error: null,
  })

  const fetchData = useCallback(async () => {
    setState(prev => ({ ...prev, loading: true, error: null }))
    try {
      const data = await fetchFn()
      setState({ data, loading: false, error: null })
    } catch (error) {
      setState({ data: null, loading: false, error: error as Error })
    }
  }, [fetchFn])

  useEffect(() => {
    fetchData()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps)

  return { ...state, refetch: fetchData }
}

export function usePolling<T>(
  fetchFn: () => Promise<T>,
  intervalMs: number = 60000,
  deps: unknown[] = []
): UseApiResult<T> {
  const result = useApi(fetchFn, deps)

  useEffect(() => {
    const interval = setInterval(() => {
      result.refetch()
    }, intervalMs)

    return () => clearInterval(interval)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [intervalMs, ...deps])

  return result
}

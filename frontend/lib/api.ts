import useSWR from 'swr'

const fetcher = (url: string) => fetch(url).then(res => res.json())

export function useProperties(params = {}) {
  const query = new URLSearchParams(params as any).toString()
  const base = process.env.NEXT_PUBLIC_API_BASE_URL || ''
  const url = base ? `${base}/api/properties/?${query}` : `/api/properties/?${query}`
  const { data, error } = useSWR(url, fetcher)
  return {
    properties: data?.items || [],
    total: data?.total || 0,
    isLoading: !error && !data,
    isError: error
  }
}

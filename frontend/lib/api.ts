const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'

export interface PropertyImage {
  url: string
  caption?: string
}

export interface PropertyAmenity {
  name: string
  available: boolean
}

export interface Property {
  id: string
  source: string
  external_id: string
  title: string
  description?: string
  property_type: string
  price: number
  price_per_sqft?: number
  area_sqft: number
  bedrooms?: number
  bathrooms?: number
  address: string
  locality: string
  city: string
  latitude?: number
  longitude?: number
  listing_url: string
  image_urls?: PropertyImage[]
  amenities?: PropertyAmenity[]
  created_at: string
  updated_at: string
  last_seen_at: string
}

export interface PropertyListResponse {
  total: number
  items: Property[]
  limit: number
  offset: number
}

export interface PropertyFilters {
  locality?: string
  min_price?: number
  max_price?: number
  bedrooms?: number
  property_type?: string
  source?: string
  include_test_data?: boolean
}

export async function fetchProperties(
  filters?: PropertyFilters
): Promise<PropertyListResponse> {
  const params = new URLSearchParams()
  params.set('limit', '100')

  if (filters) {
    if (filters.locality) params.set('locality', filters.locality)
    if (filters.min_price !== undefined) params.set('min_price', String(filters.min_price))
    if (filters.max_price !== undefined) params.set('max_price', String(filters.max_price))
    if (filters.bedrooms !== undefined) params.set('bedrooms', String(filters.bedrooms))
    if (filters.property_type) params.set('property_type', filters.property_type)
    if (filters.source) params.set('source', filters.source)
    if (filters.include_test_data !== undefined) params.set('include_test_data', String(filters.include_test_data))
  }

  const res = await fetch(`${API_BASE}/api/properties/?${params.toString()}`)
  if (!res.ok) throw new Error('Failed to fetch properties')
  return res.json()
}

export async function fetchLocalitySuggestions(q: string): Promise<string[]> {
  if (!q) return []
  const params = new URLSearchParams({ q })
  const res = await fetch(`${API_BASE}/api/properties/suggestions/localities?${params.toString()}`)
  if (!res.ok) throw new Error('Failed to fetch locality suggestions')
  return res.json()
}

export async function fetchProperty(id: string): Promise<Property> {
  const res = await fetch(`${API_BASE}/api/properties/${id}`)
  if (!res.ok) throw new Error('Property not found')
  return res.json()
}

export function formatPrice(price: number): string {
  if (price >= 10000000) {
    return `₹${(price / 10000000).toFixed(2)} Cr`
  }
  if (price >= 100000) {
    return `₹${(price / 100000).toFixed(2)} L`
  }
  return `₹${price.toLocaleString('en-IN')}`
}

export interface PropertyEvent {
  id: string
  event_type: string
  old_value: any
  new_value: any
  source: string
  created_at: string
}

export async function fetchPropertyHistory(id: string): Promise<PropertyEvent[]> {
  const res = await fetch(`${API_BASE}/api/properties/${id}/history`)
  if (!res.ok) throw new Error('Failed to fetch property history')
  return res.json()
}

export interface LocalityAnalytics {
  locality: string
  inventory_count: number
  avg_price_per_sqft: number | null
  avg_price: number | null
}

export async function fetchLocalityAnalytics(): Promise<LocalityAnalytics[]> {
  const res = await fetch(`${API_BASE}/api/analytics/locality`)
  if (!res.ok) throw new Error('Failed to fetch locality analytics')
  return res.json()
}

export interface PPSFAnalytics {
  city: string
  avg_price_per_sqft: number | null
  total_active_listings: number
}

export async function fetchPPSFAnalytics(): Promise<PPSFAnalytics> {
  const res = await fetch(`${API_BASE}/api/analytics/price-per-sqft`)
  if (!res.ok) throw new Error('Failed to fetch PPSF analytics')
  return res.json()
}

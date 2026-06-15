import React, { useEffect } from 'react'

export default function Map() {
  useEffect(() => {
    // Placeholder: integrate Google Maps JS API here using NEXT_PUBLIC_GOOGLE_MAPS_API_KEY
    // Example approach:
    // 1. Load Google Maps script with your API key
    // 2. Initialize map in a ref'ed div
    // 3. Fetch properties from `${process.env.NEXT_PUBLIC_API_BASE_URL}/api/properties`
    // 4. Render markers
  }, [])

  return (
    <div style={{ width: '100%', height: '100%', background: '#e5e7eb', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
      <div style={{ color: '#374151' }}>Map placeholder — add Google Maps integration</div>
    </div>
  )
}

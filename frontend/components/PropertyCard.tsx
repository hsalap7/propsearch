import React from 'react'

export default function PropertyCard({ property }: { property: any }) {
  return (
    <div style={{ border: '1px solid #e5e7eb', padding: 12, borderRadius: 8, background: '#fff' }}>
      <h3 style={{ margin: 0 }}>{property.title}</h3>
      <p style={{ margin: '6px 0' }}>{property.locality} — ₹{property.price?.toLocaleString()}</p>
    </div>
  )
}

'use client'

import React, { useEffect, useState } from 'react'
import { Property, PropertyEvent, fetchPropertyHistory, formatPrice } from '../lib/api'

interface PropertyCardProps {
  property: Property
  selected: boolean
  onClick: () => void
}

export default function PropertyCard({ property, selected, onClick }: PropertyCardProps) {
  const [history, setHistory] = useState<PropertyEvent[]>([])
  const [loadingHistory, setLoadingHistory] = useState(false)

  useEffect(() => {
    if (selected) {
      setLoadingHistory(true)
      fetchPropertyHistory(property.id)
        .then(data => setHistory(data))
        .catch(err => console.error(err))
        .finally(() => setLoadingHistory(false))
    }
  }, [selected, property.id])

  return (
    <div
      className={`property-card${selected ? ' selected' : ''}`}
      onClick={onClick}
    >
      <div className="property-card-header">
        <div className="property-card-title">{property.title}</div>
        <div className="property-card-price">{formatPrice(property.price)}</div>
      </div>

      <div className="property-card-details">
        {property.bedrooms && <span>🛏️ {property.bedrooms} BHK</span>}
        {property.bathrooms && <span>🚿 {property.bathrooms} Bath</span>}
        {property.area_sqft && <span>📐 {property.area_sqft.toLocaleString()} sqft</span>}
        {property.price_per_sqft && <span>💰 ₹{Math.round(property.price_per_sqft)}/sqft</span>}
      </div>

      <div className="property-card-footer">
        <span className="property-card-locality">📍 {property.locality}</span>
        <div style={{ display: 'flex', gap: '4px' }}>
          {/* Support dynamic property.status and confidence_score? Yes, but fallback if not in TS interface yet */}
          <span className="badge badge-type">{property.property_type}</span>
          <span className="badge badge-source">{property.source}</span>
          {(property as any).confidence_score !== undefined && (
            <span className="badge" style={{ background: '#e2e8f0', color: '#475569' }}>
              Score: {(property as any).confidence_score}
            </span>
          )}
        </div>
      </div>

      {selected && (
        <div className="property-card-history" style={{ marginTop: '12px', borderTop: '1px solid #e2e8f0', paddingTop: '12px' }}>
          <h4 style={{ margin: '0 0 8px 0', fontSize: '14px', color: '#334155' }}>Timeline</h4>
          {loadingHistory ? (
            <div style={{ fontSize: '12px', color: '#64748b' }}>Loading history...</div>
          ) : history.length > 0 ? (
            <ul style={{ margin: 0, paddingLeft: '16px', fontSize: '12px', color: '#475569' }}>
              {history.map(event => (
                <li key={event.id} style={{ marginBottom: '4px' }}>
                  <strong style={{ color: '#0f172a' }}>{new Date(event.created_at).toLocaleDateString()}</strong>: {event.event_type}
                  {event.event_type === 'PRICE_CHANGED' && (
                    <span> ({formatPrice(event.old_value.price)} → {formatPrice(event.new_value.price)})</span>
                  )}
                </li>
              ))}
            </ul>
          ) : (
            <div style={{ fontSize: '12px', color: '#64748b' }}>No changes recorded.</div>
          )}
        </div>
      )}
    </div>
  )
}

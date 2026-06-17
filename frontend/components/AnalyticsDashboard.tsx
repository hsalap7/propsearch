'use client'

import React, { useEffect, useState } from 'react'
import { LocalityAnalytics, PPSFAnalytics, fetchLocalityAnalytics, fetchPPSFAnalytics } from '../lib/api'

export default function AnalyticsDashboard() {
  const [localities, setLocalities] = useState<LocalityAnalytics[]>([])
  const [ppsf, setPpsf] = useState<PPSFAnalytics | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([
      fetchLocalityAnalytics(),
      fetchPPSFAnalytics()
    ])
      .then(([locData, ppsfData]) => {
        setLocalities(locData)
        setPpsf(ppsfData)
      })
      .catch(err => console.error("Analytics fetch failed:", err))
      .finally(() => setLoading(false))
  }, [])

  if (loading) {
    return <div style={{ padding: '24px' }}>Loading Analytics...</div>
  }

  return (
    <div style={{ padding: '24px', backgroundColor: '#f8fafc', height: '100%', overflowY: 'auto' }}>
      <h2 style={{ fontSize: '24px', fontWeight: 'bold', marginBottom: '24px', color: '#0f172a' }}>City Analytics: Bangalore</h2>
      
      {ppsf && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px', marginBottom: '32px' }}>
          <div style={{ background: 'white', padding: '20px', borderRadius: '12px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
            <div style={{ fontSize: '14px', color: '#64748b', marginBottom: '8px' }}>Total Active Listings</div>
            <div style={{ fontSize: '32px', fontWeight: 'bold', color: '#0f172a' }}>{ppsf.total_active_listings.toLocaleString()}</div>
          </div>
          <div style={{ background: 'white', padding: '20px', borderRadius: '12px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
            <div style={{ fontSize: '14px', color: '#64748b', marginBottom: '8px' }}>City Avg Price/Sqft</div>
            <div style={{ fontSize: '32px', fontWeight: 'bold', color: '#2563eb' }}>
              ₹{ppsf.avg_price_per_sqft ? Math.round(ppsf.avg_price_per_sqft).toLocaleString() : '--'}
            </div>
          </div>
        </div>
      )}

      <h3 style={{ fontSize: '18px', fontWeight: 'bold', marginBottom: '16px', color: '#334155' }}>Locality Trends</h3>
      
      <div style={{ background: 'white', borderRadius: '12px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', overflow: 'hidden' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
          <thead style={{ background: '#f1f5f9' }}>
            <tr>
              <th style={{ padding: '12px 16px', fontWeight: '600', color: '#475569', borderBottom: '1px solid #e2e8f0' }}>Locality</th>
              <th style={{ padding: '12px 16px', fontWeight: '600', color: '#475569', borderBottom: '1px solid #e2e8f0' }}>Inventory</th>
              <th style={{ padding: '12px 16px', fontWeight: '600', color: '#475569', borderBottom: '1px solid #e2e8f0' }}>Avg Price/Sqft</th>
              <th style={{ padding: '12px 16px', fontWeight: '600', color: '#475569', borderBottom: '1px solid #e2e8f0' }}>Avg Total Price</th>
            </tr>
          </thead>
          <tbody>
            {localities.map((loc, i) => (
              <tr key={loc.locality} style={{ borderBottom: i === localities.length - 1 ? 'none' : '1px solid #e2e8f0' }}>
                <td style={{ padding: '12px 16px', color: '#0f172a', fontWeight: '500' }}>{loc.locality}</td>
                <td style={{ padding: '12px 16px', color: '#475569' }}>{loc.inventory_count}</td>
                <td style={{ padding: '12px 16px', color: '#2563eb', fontWeight: '500' }}>
                  {loc.avg_price_per_sqft ? `₹${Math.round(loc.avg_price_per_sqft).toLocaleString()}` : '--'}
                </td>
                <td style={{ padding: '12px 16px', color: '#475569' }}>
                  {loc.avg_price ? `₹${(loc.avg_price / 100000).toFixed(2)} L` : '--'}
                </td>
              </tr>
            ))}
            {localities.length === 0 && (
              <tr>
                <td colSpan={4} style={{ padding: '24px', textAlign: 'center', color: '#94a3b8' }}>No localities found</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}

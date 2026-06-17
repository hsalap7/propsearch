'use client'

import React, { useState, useEffect, useCallback } from 'react'
import dynamic from 'next/dynamic'
import SearchPanel from '../components/SearchPanel'
import PropertyList from '../components/PropertyList'
import { fetchProperties, Property, PropertyFilters } from '../lib/api'

import AnalyticsDashboard from '../components/AnalyticsDashboard'

const Map = dynamic(() => import('../components/Map'), { ssr: false })

export default function Home() {
  const [properties, setProperties] = useState<Property[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const [activeTab, setActiveTab] = useState<'map' | 'analytics'>('map')

  const loadProperties = useCallback(async (filters?: PropertyFilters) => {
    setLoading(true)
    try {
      const data = await fetchProperties(filters)
      setProperties(data.items)
      setTotal(data.total)
    } catch (err) {
      console.error('Failed to fetch properties:', err)
      setProperties([])
      setTotal(0)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    loadProperties({ include_test_data: false })
  }, [loadProperties])

  const handleSearch = useCallback(
    (filters: PropertyFilters) => {
      setSelectedId(null)
      loadProperties(filters)
    },
    [loadProperties]
  )

  return (
    <>
      <header className="header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
          <div className="header-title">
            <span className="icon">🏠</span> PropSearch Bangalore
          </div>
          <div style={{ display: 'flex', gap: '10px', background: '#e2e8f0', padding: '4px', borderRadius: '8px' }}>
            <button 
              onClick={() => setActiveTab('map')}
              style={{ padding: '6px 12px', border: 'none', background: activeTab === 'map' ? 'white' : 'transparent', borderRadius: '6px', fontWeight: activeTab === 'map' ? 'bold' : 'normal', cursor: 'pointer', color: '#0f172a' }}
            >
              Map View
            </button>
            <button 
              onClick={() => setActiveTab('analytics')}
              style={{ padding: '6px 12px', border: 'none', background: activeTab === 'analytics' ? 'white' : 'transparent', borderRadius: '6px', fontWeight: activeTab === 'analytics' ? 'bold' : 'normal', cursor: 'pointer', color: '#0f172a' }}
            >
              Analytics
            </button>
          </div>
        </div>
        <div className="header-stats">
          <span>
            <span className="count">{total}</span> properties found
          </span>
        </div>
      </header>
      <div className="app-layout">
        {activeTab === 'map' ? (
          <>
            <div className="sidebar">
              <SearchPanel onSearch={handleSearch} loading={loading} />
              <PropertyList
                properties={properties}
                total={total}
                loading={loading}
                selectedId={selectedId}
                onSelectProperty={setSelectedId}
              />
            </div>
            <div className="map-container">
              <Map
                properties={properties}
                selectedId={selectedId}
                onSelectProperty={setSelectedId}
              />
            </div>
          </>
        ) : (
          <div style={{ width: '100%', height: '100%' }}>
            <AnalyticsDashboard />
          </div>
        )}
      </div>
    </>
  )
}

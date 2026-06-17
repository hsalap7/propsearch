'use client'

import React, { useState, useEffect } from 'react'
import { PropertyFilters, fetchLocalitySuggestions } from '../lib/api'

interface SearchPanelProps {
  onSearch: (filters: PropertyFilters) => void
  loading: boolean
}

export default function SearchPanel({ onSearch, loading }: SearchPanelProps) {
  const [locality, setLocality] = useState('')
  const [minPrice, setMinPrice] = useState('')
  const [maxPrice, setMaxPrice] = useState('')
  const [bedrooms, setBedrooms] = useState<number | null>(null)
  const [propertyType, setPropertyType] = useState('')
  const [source, setSource] = useState('')
  const [includeTestData, setIncludeTestData] = useState(false)
  const [suggestions, setSuggestions] = useState<string[]>([])

  useEffect(() => {
    if (locality.length > 1) {
      const timer = setTimeout(() => {
        fetchLocalitySuggestions(locality).then(setSuggestions).catch(console.error)
      }, 300)
      return () => clearTimeout(timer)
    } else {
      setSuggestions([])
    }
  }, [locality])

  const handleSearch = () => {
    const filters: PropertyFilters = {}
    if (locality.trim()) filters.locality = locality.trim()
    if (minPrice) filters.min_price = Number(minPrice)
    if (maxPrice) filters.max_price = Number(maxPrice)
    if (bedrooms !== null) filters.bedrooms = bedrooms
    if (propertyType) filters.property_type = propertyType
    if (source) filters.source = source
    filters.include_test_data = includeTestData
    onSearch(filters)
  }

  const handleClear = () => {
    setLocality('')
    setMinPrice('')
    setMaxPrice('')
    setBedrooms(null)
    setPropertyType('')
    setSource('')
    setIncludeTestData(false)
    onSearch({ include_test_data: false })
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') handleSearch()
  }

  return (
    <div className="search-panel">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h2>🔍 Search Properties</h2>
        <label style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.9rem', cursor: 'pointer' }}>
          <input
            type="checkbox"
            checked={includeTestData}
            onChange={(e) => setIncludeTestData(e.target.checked)}
            style={{ width: '16px', height: '16px', accentColor: 'var(--primary)' }}
          />
          Show test data
        </label>
      </div>
      <div className="filter-grid">
        <div className="filter-group full-width">
          <label>Locality</label>
          <input
            type="text"
            list="locality-suggestions"
            placeholder="e.g. Koramangala, Whitefield..."
            value={locality}
            onChange={e => setLocality(e.target.value)}
            onKeyDown={handleKeyDown}
          />
          <datalist id="locality-suggestions">
            {suggestions.map((s, idx) => (
              <option key={idx} value={s} />
            ))}
          </datalist>
        </div>

        <div className="filter-group">
          <label>Min Price (₹)</label>
          <input
            type="number"
            placeholder="Min"
            value={minPrice}
            onChange={e => setMinPrice(e.target.value)}
            onKeyDown={handleKeyDown}
          />
        </div>

        <div className="filter-group">
          <label>Max Price (₹)</label>
          <input
            type="number"
            placeholder="Max"
            value={maxPrice}
            onChange={e => setMaxPrice(e.target.value)}
            onKeyDown={handleKeyDown}
          />
        </div>

        <div className="filter-group full-width">
          <label>Bedrooms</label>
          <div className="bedrooms-selector">
            {[
              { label: 'Any', value: null },
              { label: '1 BHK', value: 1 },
              { label: '2 BHK', value: 2 },
              { label: '3 BHK', value: 3 },
              { label: '4+ BHK', value: 4 },
            ].map(opt => (
              <button
                key={opt.label}
                className={`bedroom-btn${bedrooms === opt.value ? ' active' : ''}`}
                onClick={() => setBedrooms(opt.value)}
                type="button"
              >
                {opt.label}
              </button>
            ))}
          </div>
        </div>

        <div className="filter-group full-width">
          <label>Property Type</label>
          <select
            value={propertyType}
            onChange={e => setPropertyType(e.target.value)}
          >
            <option value="">All Types</option>
            <option value="apartment">Apartment</option>
            <option value="villa">Villa</option>
            <option value="townhouse">Townhouse</option>
            <option value="independent house">Independent House</option>
          </select>
        </div>

        <div className="filter-group full-width">
          <label>Source</label>
          <select
            value={source}
            onChange={e => setSource(e.target.value)}
          >
            <option value="">All Sources</option>
            <option value="prestige">Prestige Group</option>
            <option value="housing.com">Housing.com</option>
            <option value="magicbricks.com">MagicBricks</option>
            <option value="nobroker.com">NoBroker</option>
            <option value="99acres.com">99acres</option>
            <option value="csv_upload">CSV Upload</option>
          </select>
        </div>
      </div>

      <div className="search-actions">
        <button className="btn-search" onClick={handleSearch} disabled={loading}>
          {loading ? '⏳ Searching...' : '🔍 Search'}
        </button>
        <button className="btn-clear" onClick={handleClear} type="button">
          Clear
        </button>
      </div>
    </div>
  )
}

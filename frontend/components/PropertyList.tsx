'use client'

import React from 'react'
import { Property } from '../lib/api'
import PropertyCard from './PropertyCard'

interface PropertyListProps {
  properties: Property[]
  total: number
  loading: boolean
  selectedId: string | null
  onSelectProperty: (id: string) => void
}

export default function PropertyList({
  properties,
  total,
  loading,
  selectedId,
  onSelectProperty,
}: PropertyListProps) {
  if (loading) {
    return (
      <div className="property-list">
        <div className="loading-container">
          <div className="spinner" />
          <span>Loading properties...</span>
        </div>
      </div>
    )
  }

  if (properties.length === 0) {
    return (
      <div className="property-list">
        <div className="empty-state">
          <div className="icon">🏘️</div>
          <p>No properties found.<br />Try adjusting your filters.</p>
        </div>
      </div>
    )
  }

  return (
    <div className="property-list">
      <div className="list-header">
        Showing <span className="count">{properties.length}</span> of{' '}
        <span className="count">{total}</span> properties
      </div>
      {properties.map(property => (
        <PropertyCard
          key={property.id}
          property={property}
          selected={property.id === selectedId}
          onClick={() => onSelectProperty(property.id)}
        />
      ))}
    </div>
  )
}

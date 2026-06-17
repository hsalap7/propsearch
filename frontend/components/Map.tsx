'use client'

import React, { useEffect, useRef } from 'react'
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet'
import L from 'leaflet'
import { Property, formatPrice } from '../lib/api'

// Fix default marker icon (webpack breaks leaflet's default icon paths)
const defaultIcon = L.icon({
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
})

const selectedIcon = L.icon({
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
  iconSize: [30, 49],
  iconAnchor: [15, 49],
  popupAnchor: [1, -40],
  shadowSize: [49, 49],
  className: 'selected-marker',
})

interface MapProps {
  properties: Property[]
  selectedId: string | null
  onSelectProperty: (id: string) => void
}

function FitBounds({ properties }: { properties: Property[] }) {
  const map = useMap()
  const prevLengthRef = useRef(0)

  useEffect(() => {
    // Only fit bounds when properties change (not on every render)
    if (properties.length > 0 && properties.length !== prevLengthRef.current) {
      const validProps = properties.filter(p => p.latitude && p.longitude)
      if (validProps.length > 0) {
        const bounds = L.latLngBounds(
          validProps.map(p => [p.latitude!, p.longitude!] as [number, number])
        )
        map.fitBounds(bounds, { padding: [30, 30], maxZoom: 14 })
      }
    }
    prevLengthRef.current = properties.length
  }, [properties, map])

  return null
}

export default function Map({ properties, selectedId, onSelectProperty }: MapProps) {
  const center: [number, number] = [12.9716, 77.5946]
  const [map, setMap] = React.useState<L.Map | null>(null)

  React.useEffect(() => {
    return () => {
      if (map) {
        map.remove()
      }
    }
  }, [map])

  return (
    <MapContainer
      center={center}
      zoom={12}
      style={{ width: '100%', height: '100%' }}
      zoomControl={true}
      ref={setMap}
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      <FitBounds properties={properties} />
      {properties
        .filter(p => p.latitude && p.longitude)
        .map(property => (
          <Marker
            key={property.id}
            position={[property.latitude!, property.longitude!]}
            icon={property.id === selectedId ? selectedIcon : defaultIcon}
            eventHandlers={{
              click: () => onSelectProperty(property.id),
            }}
          >
            <Popup>
              <div className="popup-content">
                <h3>{property.title}</h3>
                <div className="popup-price">{formatPrice(property.price)}</div>
                <div className="popup-details">
                  {property.bedrooms && `${property.bedrooms} BHK`}
                  {property.bathrooms && ` · ${property.bathrooms} Bath`}
                  {property.area_sqft && ` · ${property.area_sqft.toLocaleString()} sqft`}
                </div>
                <div className="popup-details">📍 {property.locality}</div>
                <a
                  href={property.listing_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="popup-link"
                >
                  View listing →
                </a>
              </div>
            </Popup>
          </Marker>
        ))}
    </MapContainer>
  )
}

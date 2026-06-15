from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class PropertyImageSchema(BaseModel):
    url: str
    caption: Optional[str] = None


class PropertyAmenitySchema(BaseModel):
    name: str
    available: bool = True


class PropertyBase(BaseModel):
    source: str
    external_id: str
    title: str
    description: Optional[str] = None
    property_type: str
    price: int
    price_per_sqft: Optional[float] = None
    area_sqft: int
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    address: str
    locality: str
    city: str = "Bangalore"
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    listing_url: str
    image_urls: Optional[list[PropertyImageSchema]] = None
    amenities: Optional[list[PropertyAmenitySchema]] = None


class PropertyCreate(PropertyBase):
    pass


class PropertyUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[int] = None
    price_per_sqft: Optional[float] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    image_urls: Optional[list[PropertyImageSchema]] = None
    amenities: Optional[list[PropertyAmenitySchema]] = None


class PropertyResponse(PropertyBase):
    id: str
    created_at: datetime
    updated_at: datetime
    last_seen_at: datetime

    class Config:
        from_attributes = True


class PropertyListResponse(BaseModel):
    total: int
    items: list[PropertyResponse]
    limit: int
    offset: int


class HealthResponse(BaseModel):
    status: str

from datetime import datetime
from typing import Optional
from uuid import uuid4

from geoalchemy2 import Geography
from sqlalchemy import JSON, TIMESTAMP, BigInteger, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class Property(Base):
    """Property listing model with geospatial support."""

    __tablename__ = "properties"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid4())
    )
    source: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    external_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    property_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    price: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    price_per_sqft: Mapped[Optional[float]] = mapped_column(nullable=True)
    area_sqft: Mapped[int] = mapped_column(Integer, nullable=False)
    bedrooms: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    bathrooms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    address: Mapped[str] = mapped_column(Text, nullable=False)
    locality: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    city: Mapped[str] = mapped_column(String(100), nullable=False, default="Bangalore")
    latitude: Mapped[float] = mapped_column(nullable=False)
    longitude: Mapped[float] = mapped_column(nullable=False)
    location: Mapped[str] = mapped_column(
        Geography(geometry_type="POINT", srid=4326), nullable=False
    )
    listing_url: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    image_urls: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    amenities: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now()
    )

    def __repr__(self) -> str:
        return f"<Property(id={self.id}, title={self.title}, locality={self.locality})>"

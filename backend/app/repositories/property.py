from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select
from geoalchemy2.functions import ST_DWithin

from app.models.property import Property
from app.schemas.property import PropertyCreate


class PropertyRepository:
    """Repository for property data access."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, property_data: PropertyCreate) -> Property:
        """Create a new property."""
        location = (
            f"POINT({property_data.longitude} {property_data.latitude})"
            if property_data.longitude is not None and property_data.latitude is not None
            else None
        )

        property_obj = Property(
            source=property_data.source,
            external_id=property_data.external_id,
            title=property_data.title,
            description=property_data.description,
            property_type=property_data.property_type,
            price=property_data.price,
            price_per_sqft=property_data.price_per_sqft,
            area_sqft=property_data.area_sqft,
            bedrooms=property_data.bedrooms,
            bathrooms=property_data.bathrooms,
            address=property_data.address,
            locality=property_data.locality,
            city=property_data.city,
            latitude=property_data.latitude,
            longitude=property_data.longitude,
            location=location,
            listing_url=property_data.listing_url,
            image_urls=(
                [img.model_dump() for img in property_data.image_urls]
                if property_data.image_urls
                else None
            ),
            amenities=(
                [am.model_dump() for am in property_data.amenities]
                if property_data.amenities
                else None
            ),
        )

        self.session.add(property_obj)
        await self.session.commit()
        await self.session.refresh(property_obj)
        return property_obj

    async def get_by_id(self, property_id: str) -> Property:
        """Get property by ID."""
        stmt = select(Property).where(Property.id == property_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list(
        self,
        limit: int = 50,
        offset: int = 0,
        locality: str = None,
        min_price: int = None,
        max_price: int = None,
        bedrooms: int = None,
        property_type: str = None,
        source: str = None,
        include_test_data: bool = True,
    ) -> tuple[list[Property], int]:
        """List properties with optional filters."""
        stmt = select(Property)

        if not include_test_data:
            stmt = stmt.where(Property.is_test_data == False)
        if locality:
            stmt = stmt.where(Property.locality.ilike(f"%{locality}%"))
        if min_price is not None:
            stmt = stmt.where(Property.price >= min_price)
        if max_price is not None:
            stmt = stmt.where(Property.price <= max_price)
        if bedrooms is not None:
            stmt = stmt.where(Property.bedrooms == bedrooms)
        if property_type:
            stmt = stmt.where(Property.property_type.ilike(f"%{property_type}%"))
        if source:
            stmt = stmt.where(Property.source == source)

        count_stmt = select(func.count()).select_from(Property)
        if not include_test_data:
            count_stmt = count_stmt.where(Property.is_test_data == False)
        if locality:
            count_stmt = count_stmt.where(Property.locality.ilike(f"%{locality}%"))
        if min_price is not None:
            count_stmt = count_stmt.where(Property.price >= min_price)
        if max_price is not None:
            count_stmt = count_stmt.where(Property.price <= max_price)
        if bedrooms is not None:
            count_stmt = count_stmt.where(Property.bedrooms == bedrooms)
        if property_type:
            count_stmt = count_stmt.where(Property.property_type.ilike(f"%{property_type}%"))
        if source:
            count_stmt = count_stmt.where(Property.source == source)

        total = await self.session.execute(count_stmt)
        total_count = total.scalar()

        stmt = stmt.limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return result.scalars().all(), total_count

    async def get_locality_suggestions(self, prefix: str, limit: int = 10) -> list[str]:
        """Get locality suggestions based on a prefix."""
        stmt = (
            select(Property.locality)
            .where(Property.locality.ilike(f"{prefix}%"))
            .distinct()
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def nearby(
        self, latitude: float, longitude: float, radius_meters: int = 5000
    ) -> list[Property]:
        """Find properties nearby using PostGIS."""
        point = f"POINT({longitude} {latitude})"
        stmt = (
            select(Property)
            .where(ST_DWithin(Property.location, point, radius_meters))
            .limit(100)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

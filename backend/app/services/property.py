from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.property import PropertyRepository
from app.schemas.property import PropertyCreate, PropertyResponse, PropertyListResponse


class PropertyService:
    """Service layer for property business logic."""

    def __init__(self, session: AsyncSession):
        self.repository = PropertyRepository(session)

    async def create_property(self, property_data: PropertyCreate) -> PropertyResponse:
        """Create a new property."""
        property_obj = await self.repository.create(property_data)
        return PropertyResponse.model_validate(property_obj)

    async def get_property(self, property_id: str) -> PropertyResponse:
        """Get property by ID."""
        property_obj = await self.repository.get_by_id(property_id)
        if not property_obj:
            raise ValueError(f"Property with ID {property_id} not found")
        return PropertyResponse.model_validate(property_obj)

    async def list_properties(
        self,
        limit: int = 50,
        offset: int = 0,
        locality: str = None,
        min_price: int = None,
        max_price: int = None,
        bedrooms: int = None,
        property_type: str = None,
    ) -> PropertyListResponse:
        """List properties with filters."""
        properties, total = await self.repository.list(
            limit=limit,
            offset=offset,
            locality=locality,
            min_price=min_price,
            max_price=max_price,
            bedrooms=bedrooms,
            property_type=property_type,
        )
        return PropertyListResponse(
            total=total,
            items=[PropertyResponse.model_validate(p) for p in properties],
            limit=limit,
            offset=offset,
        )

    async def find_nearby(
        self, latitude: float, longitude: float, radius_meters: int = 5000
    ) -> list[PropertyResponse]:
        """Find properties nearby."""
        properties = await self.repository.nearby(latitude, longitude, radius_meters)
        return [PropertyResponse.model_validate(p) for p in properties]

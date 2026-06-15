from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db
from app.schemas.property import (
    PropertyCreate,
    PropertyResponse,
    PropertyListResponse,
)
from app.services.property import PropertyService

router = APIRouter(prefix="/api/properties", tags=["properties"])


@router.post("/", response_model=PropertyResponse)
async def create_property(
    property_data: PropertyCreate,
    session: AsyncSession = Depends(get_db),
):
    """Create a new property."""
    service = PropertyService(session)
    return await service.create_property(property_data)


@router.get("/", response_model=PropertyListResponse)
async def list_properties(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    locality: str = Query(None),
    min_price: int = Query(None),
    max_price: int = Query(None),
    bedrooms: int = Query(None),
    property_type: str = Query(None),
    session: AsyncSession = Depends(get_db),
):
    """List properties with optional filters."""
    service = PropertyService(session)
    return await service.list_properties(
        limit=limit,
        offset=offset,
        locality=locality,
        min_price=min_price,
        max_price=max_price,
        bedrooms=bedrooms,
        property_type=property_type,
    )


@router.get("/{property_id}", response_model=PropertyResponse)
async def get_property(
    property_id: str,
    session: AsyncSession = Depends(get_db),
):
    """Get property details by ID."""
    service = PropertyService(session)
    try:
        return await service.get_property(property_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/nearby/search", response_model=list[PropertyResponse])
async def nearby_properties(
    lat: float = Query(...),
    lng: float = Query(...),
    radius_meters: int = Query(5000, ge=100),
    session: AsyncSession = Depends(get_db),
):
    """Find properties nearby using geospatial search."""
    service = PropertyService(session)
    return await service.find_nearby(lat, lng, radius_meters)

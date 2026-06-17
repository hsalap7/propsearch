from fastapi import APIRouter, Depends
from sqlalchemy import select, func, text
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any

from app.core.dependencies import get_db
from app.models.property import Property

router = APIRouter()

@router.get("/locality", response_model=list[dict[str, Any]])
async def analytics_locality(db: AsyncSession = Depends(get_db)):
    """Returns aggregated metrics grouped by locality."""
    stmt = (
        select(
            Property.locality,
            func.count(Property.id).label("inventory_count"),
            func.avg(Property.price_per_sqft).label("avg_price_per_sqft"),
            func.avg(Property.price).label("avg_price")
        )
        .where(Property.status == "active")
        .group_by(Property.locality)
        .order_by(func.count(Property.id).desc())
    )
    result = await db.execute(stmt)
    
    data = []
    for row in result:
        data.append({
            "locality": row.locality,
            "inventory_count": row.inventory_count,
            "avg_price_per_sqft": round(row.avg_price_per_sqft, 2) if row.avg_price_per_sqft else None,
            "avg_price": float(row.avg_price) if row.avg_price else None
        })
    return data

@router.get("/price-per-sqft")
async def analytics_ppsf(db: AsyncSession = Depends(get_db)):
    """Computes overall average PPSF and count across the city."""
    stmt = select(
        func.avg(Property.price_per_sqft).label("avg_ppsf"),
        func.count(Property.id).label("total_listings")
    ).where(Property.status == "active")
    
    result = await db.execute(stmt)
    row = result.first()
    
    return {
        "city": "Bangalore",
        "avg_price_per_sqft": round(row.avg_ppsf, 2) if row and row.avg_ppsf else None,
        "total_active_listings": row.total_listings if row else 0
    }

@router.get("/heatmap")
async def analytics_heatmap(db: AsyncSession = Depends(get_db)):
    """Returns lightweight GeoJSON points with price weights for mapping."""
    stmt = select(
        Property.id,
        Property.latitude,
        Property.longitude,
        Property.price,
        Property.price_per_sqft
    ).where(
        Property.status == "active",
        Property.latitude.isnot(None),
        Property.longitude.isnot(None)
    )
    
    result = await db.execute(stmt)
    
    features = []
    for row in result:
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [row.longitude, row.latitude]
            },
            "properties": {
                "id": row.id,
                "price": row.price,
                "weight": row.price_per_sqft or 0
            }
        })
        
    return {
        "type": "FeatureCollection",
        "features": features
    }

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db
from app.models.ingestion import PropertyDuplicate
from app.models.property import Property

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/stats")
async def ingestion_stats(session: AsyncSession = Depends(get_db)) -> dict[str, int]:
    properties = await session.scalar(select(func.count()).select_from(Property)) or 0
    mappings = (
        await session.scalar(select(func.count()).select_from(PropertyDuplicate)) or 0
    )
    stats = {"properties": properties, "duplicates": max(mappings - properties, 0)}
    for source in ("housing", "nobroker", "magicbricks", "99acres"):
        stats[source] = (
            await session.scalar(
                select(func.count())
                .select_from(PropertyDuplicate)
                .where(PropertyDuplicate.source == source)
            )
            or 0
        )
    return stats

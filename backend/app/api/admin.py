from typing import Any
from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db
from app.models.ingestion import JobRun, PropertyDuplicate
from app.models.property import Property

router = APIRouter()

@router.get("/jobs", response_model=list[dict[str, Any]])
async def get_jobs(session: AsyncSession = Depends(get_db)):
    stmt = select(JobRun).order_by(JobRun.started_at.desc()).limit(50)
    result = await session.execute(stmt)
    jobs = result.scalars().all()
    return [
        {
            "id": job.id,
            "source": job.source,
            "status": job.status,
            "started_at": job.started_at.isoformat() if job.started_at else None,
            "ended_at": job.ended_at.isoformat() if job.ended_at else None,
            "listings_collected": job.listings_collected,
            "listings_saved": job.listings_saved,
            "failures": job.failures,
            "success_rate": job.success_rate,
            "error": job.error,
        }
        for job in jobs
    ]

@router.get("/stats")
async def get_stats(session: AsyncSession = Depends(get_db)):
    prop_count = await session.scalar(select(func.count(Property.id)))
    dup_count = await session.scalar(select(func.count(PropertyDuplicate.id)))
    
    # Source breakdown
    stmt = select(Property.source, func.count(Property.id)).group_by(Property.source)
    source_results = await session.execute(stmt)
    sources = {row[0]: row[1] for row in source_results}

    return {
        "properties": prop_count,
        "duplicates": dup_count,
        "sources": sources
    }

@router.get("/sources")
async def get_sources():
    from ingestion.plugins.registry import SOURCES
    return {"registered_sources": list(SOURCES.keys())}

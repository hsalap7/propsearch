"""Scheduled collector jobs."""

import asyncio

from apscheduler.schedulers.blocking import BlockingScheduler
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.config import settings
from ingestion.registry import COLLECTORS

SCHEDULE_HOURS = {
    "housing": 6,
    "magicbricks": 6,
    "nobroker": 12,
    "99acres": 12,
}


async def collect_source(source: str) -> None:
    engine = create_async_engine(settings.database_url)
    try:
        async with async_sessionmaker(engine, expire_on_commit=False)() as session:
            await COLLECTORS[source](session).ingest()
    finally:
        await engine.dispose()


def main() -> None:
    scheduler = BlockingScheduler(timezone="UTC")
    for source, hours in SCHEDULE_HOURS.items():
        scheduler.add_job(
            lambda name=source: asyncio.run(collect_source(name)),
            "interval",
            hours=hours,
            id=f"collect-{source}",
            max_instances=1,
            coalesce=True,
        )
    scheduler.start()


if __name__ == "__main__":
    main()

import argparse
import asyncio
import logging
from typing import Type

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.models.ingestion import JobRun
from ingestion.core.session import SessionManager
from ingestion.plugins.registry import SOURCES
from ingestion.plugins.base import SourcePlugin

logging.basicConfig(level=logging.INFO, format="%(levelname)-8s %(message)s")
logger = logging.getLogger(__name__)


async def run_plugin(source_name: str, PluginClass: Type[SourcePlugin]) -> None:
    logger.info(f"Starting execution for source: {source_name}")
    
    engine = create_async_engine(settings.database_url, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as db:
        # Create a JobRun
        job = JobRun(source=source_name, status="running")
        db.add(job)
        await db.commit()

        try:
            # Initialize engines
            session_manager = SessionManager(db)
            plugin = PluginClass(db=db, session_manager=session_manager)

            # Pipeline Execution
            logger.info("-> Authenticating...")
            await plugin.authenticate()

            logger.info("-> Collecting...")
            await plugin.collect()

            # The actual system would read RawPayloads here and run Normalization/Dedupe/Geocode
            # But for Phase 2.5, we just test that the plugin ran successfully and saved raw payload
            
            # Mark Job as completed
            job.status = "completed"
            job.listings_collected = 1 # mocked
            job.listings_saved = 1
            from datetime import datetime
            job.ended_at = datetime.utcnow()
            await db.commit()
            logger.info(f"Finished execution for source: {source_name}")

        except Exception as e:
            logger.error(f"Execution failed: {e}")
            job.status = "failed"
            job.error = str(e)
            from datetime import datetime
            job.ended_at = datetime.utcnow()
            await db.commit()


def main():
    parser = argparse.ArgumentParser(description="Run a data acquisition source plugin.")
    parser.add_argument("source", choices=list(SOURCES.keys()), help="Name of the source plugin to run")
    args = parser.parse_args()

    PluginClass = SOURCES[args.source]
    asyncio.run(run_plugin(args.source, PluginClass))


if __name__ == "__main__":
    main()

"""Run one registered property collector: python collect.py housing."""

import argparse
import asyncio

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.config import settings
from ingestion.registry import COLLECTORS


async def run(source: str) -> int:
    engine = create_async_engine(settings.database_url)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    try:
        async with session_factory() as session:
            return await COLLECTORS[source](session).ingest()
    finally:
        await engine.dispose()


def main() -> None:
    parser = argparse.ArgumentParser(description="Collect property listings")
    parser.add_argument("source", choices=sorted(COLLECTORS))
    args = parser.parse_args()
    count = asyncio.run(run(args.source))
    print(f"{args.source}: saved {count} canonical properties")


if __name__ == "__main__":
    main()

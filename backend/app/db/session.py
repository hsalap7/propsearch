from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()


async def init_db(database_url: str):
    """Initialize database engine and create tables."""
    engine = create_async_engine(
        database_url,
        echo=False,
        future=True,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    return engine


def get_sync_engine(database_url: str):
    """Get synchronous engine for Alembic migrations."""
    return create_engine(database_url, echo=False, future=True)


async def get_session(async_engine):
    """Session factory for dependency injection."""
    async_session = sessionmaker(
        async_engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        yield session

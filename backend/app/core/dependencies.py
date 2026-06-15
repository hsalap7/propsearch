from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine
from typing import AsyncGenerator

_async_engine: AsyncEngine = None


async def init_db_engine(database_url: str) -> AsyncEngine:
    """Initialize async database engine."""
    global _async_engine
    from app.db.session import init_db

    _async_engine = await init_db(database_url)
    return _async_engine


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Get database session for dependency injection."""
    if _async_engine is None:
        raise RuntimeError("Database engine not initialized")

    from app.db.session import get_session

    async for session in get_session(_async_engine):
        yield session

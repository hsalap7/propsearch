from typing import Protocol
from sqlalchemy.ext.asyncio import AsyncSession
from ingestion.core.session import SessionManager
from app.models.ingestion import RawPayload
from ingestion.schema import Listing


class SourcePlugin(Protocol):
    """
    Abstract base interface for all source plugins.
    A plugin should implement authentication, collection, and normalization.
    """
    source_name: str

    def __init__(self, db: AsyncSession, session_manager: SessionManager):
        ...

    async def authenticate(self) -> None:
        """
        Authenticate with the source and persist tokens/cookies 
        using the session manager.
        """
        ...

    async def collect(self) -> None:
        """
        Navigate the source (via Playwright or API calls),
        capturing payloads into the RawPayload store.
        """
        ...

    def normalize(self, payload: RawPayload) -> list[Listing]:
        """
        Convert a raw source-specific payload into a list of Canonical Listings.
        """
        ...

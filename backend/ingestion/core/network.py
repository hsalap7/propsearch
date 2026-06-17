import json
import logging
from typing import Callable, Coroutine, Any

from sqlalchemy.ext.asyncio import AsyncSession
from app.models.ingestion import RawPayload

logger = logging.getLogger(__name__)


class NetworkCaptureLayer:
    """Reusable Playwright interception framework to capture JSON/XHR payloads."""

    def __init__(self, db: AsyncSession, source: str):
        self.db = db
        self.source = source

    def attach_to_page(self, page) -> None:
        """Attach network interceptors to a Playwright page."""
        page.on("response", self._handle_response)

    async def _handle_response(self, response) -> None:
        """Intercept responses and save JSON payloads."""
        # Only capture fetch/xhr that might contain data
        if response.request.resource_type not in ["fetch", "xhr"]:
            return

        # Skip preflight requests or non-200 responses
        if response.status != 200:
            return

        try:
            content_type = response.headers.get("content-type", "")
            if "application/json" not in content_type:
                return

            body = await response.json()
            # Only save non-empty dictionaries or lists
            if not body:
                return

            # Save the payload
            payload_record = RawPayload(
                source=self.source,
                endpoint=response.url,
                payload_json=body,
            )
            self.db.add(payload_record)
            await self.db.commit()
            
            logger.debug(f"Captured payload from {response.url}")

        except Exception as e:
            # Safely ignore parsing errors for non-JSON or malformed responses
            await self.db.rollback()
            logger.debug(f"Failed to parse or save response from {response.url}: {e}")

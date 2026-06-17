import json
import logging
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ingestion import RawPayload
from ingestion.core.session import SessionManager
from ingestion.schema import Listing
from ingestion.plugins.base import SourcePlugin

logger = logging.getLogger(__name__)


class MockPlugin:
    source_name = "mock_source"

    def __init__(self, db: AsyncSession, session_manager: SessionManager):
        self.db = db
        self.session_manager = session_manager

    async def authenticate(self) -> None:
        logger.info("MockPlugin: Authenticating...")
        await self.session_manager.save_session(
            source=self.source_name,
            cookies=[{"name": "mock_session", "value": "12345"}],
            session_state={"authenticated": True}
        )
        logger.info("MockPlugin: Authenticated and session saved.")

    async def collect(self) -> None:
        logger.info("MockPlugin: Collecting data...")
        
        # Simulate network capture by directly saving a raw payload
        mock_data = {
            "results": [
                {
                    "id": "mock_123",
                    "title": "Beautiful Mock Apartment",
                    "price": 7500000,
                    "area": 1200,
                    "beds": 2,
                    "baths": 2,
                    "location": "Koramangala",
                    "url": "https://mock.com/123",
                    "images": ["https://mock.com/img1.jpg"]
                }
            ]
        }
        
        payload_record = RawPayload(
            source=self.source_name,
            endpoint="https://mock.com/api/search",
            payload_json=mock_data,
        )
        self.db.add(payload_record)
        await self.db.commit()
        logger.info("MockPlugin: Collection complete. Raw payload saved.")

    def normalize(self, payload: RawPayload) -> list[Listing]:
        listings = []
        data = payload.payload_json.get("results", [])
        for item in data:
            listing = Listing(
                source=self.source_name,
                external_id=item.get("id"),
                title=item.get("title"),
                property_type="residential",
                price=item.get("price"),
                area_sqft=item.get("area"),
                bedrooms=item.get("beds"),
                bathrooms=item.get("baths"),
                address=item.get("location"),
                locality=item.get("location"),
                city="Bangalore",
                image_urls=item.get("images", []),
                amenities=["Mock Amenity"],
                listing_url=item.get("url")
            )
            listings.append(listing)
        return listings

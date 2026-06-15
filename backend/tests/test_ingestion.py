from datetime import datetime, timezone

import pytest

from ingestion.base import BaseCollector
from ingestion.registry import COLLECTORS
from ingestion.schema import Listing, RawListingData
from ingestion.service import IngestionService


def listing(source: str = "housing", external_id: str = "one") -> Listing:
    return Listing(
        source=source,
        external_id=external_id,
        title="2 BHK in Indiranagar",
        price=10_000_000,
        area_sqft=1000,
        bedrooms=2,
        address="100 Main Road",
        locality="Indiranagar",
        city="Bangalore",
        latitude=12.97,
        longitude=77.64,
        image_urls=["https://example.com/a.jpg", "javascript:bad"],
        amenities=["Lift"],
        listing_url=f"https://example.com/{external_id}",
        last_seen_at=datetime.now(timezone.utc),
    )


def test_registry_contains_all_sources():
    assert set(COLLECTORS) == {"housing", "nobroker", "magicbricks", "99acres"}
    assert all(issubclass(collector, BaseCollector) for collector in COLLECTORS.values())


def test_listing_fingerprint_is_normalized_and_images_are_safe():
    first = listing()
    second = listing()
    second.address = "  100   MAIN ROAD "
    assert first.fingerprint == second.fingerprint
    assert first.image_urls == ["https://example.com/a.jpg"]


@pytest.mark.asyncio
async def test_service_stores_raw_and_deduplicates(test_session):
    service = IngestionService(test_session)
    raw = RawListingData(
        source="housing",
        external_id="one",
        listing_url="https://example.com/one",
        payload={"original": True},
    )
    assert await service.save([listing()], [raw]) == 1
    assert await service.save([listing("magicbricks", "two")]) == 0

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ingestion import CollectorLog, JobRun, PropertyDuplicate, RawListing
from app.models.property import Property
from ingestion.geocoding import Geocoder
from ingestion.schema import Listing, RawListingData


class IngestionService:
    """Central persistence, enrichment, and cross-source deduplication."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.geocoder = Geocoder(session)

    async def save_raw(self, records: list[RawListingData]) -> None:
        self.session.add_all(
            [
                RawListing(
                    source=record.source,
                    external_id=record.external_id,
                    payload={
                        "listing_url": record.listing_url,
                        "response": record.payload,
                    },
                )
                for record in records
            ]
        )
        await self.session.commit()

    async def save(
        self,
        listings: list[Listing],
        raw_records: list[RawListingData] | None = None,
    ) -> int:
        if raw_records:
            await self.save_raw(raw_records)
        saved = 0
        for listing in listings:
            geocode = await self.geocoder.geocode(listing)
            existing = await self.session.scalar(
                select(Property).where(Property.fingerprint == listing.fingerprint)
            )
            if existing:
                await self._map_duplicate(listing, existing)
                existing.last_seen_at = listing.last_seen_at
                continue

            location = None
            latitude = longitude = None
            if geocode:
                latitude, longitude = geocode.latitude, geocode.longitude
                location = f"POINT({longitude} {latitude})"
            property_obj = Property(
                **listing.model_dump(
                    exclude={"latitude", "longitude", "image_urls", "amenities"}
                ),
                fingerprint=listing.fingerprint,
                latitude=latitude,
                longitude=longitude,
                location=location,
                image_urls=listing.image_urls,
                amenities=listing.amenities,
                price_per_sqft=listing.price / listing.area_sqft,
            )
            self.session.add(property_obj)
            await self.session.flush()
            await self._map_duplicate(listing, property_obj)
            saved += 1
        await self.session.commit()
        return saved

    async def _map_duplicate(self, listing: Listing, property_obj: Property) -> None:
        mapping = await self.session.scalar(
            select(PropertyDuplicate).where(
                PropertyDuplicate.source == listing.source,
                PropertyDuplicate.external_id == listing.external_id,
            )
        )
        if not mapping:
            self.session.add(
                PropertyDuplicate(
                    source=listing.source,
                    external_id=listing.external_id,
                    property_id=property_obj.id,
                    fingerprint=listing.fingerprint,
                )
            )

    async def start_job(self, source: str) -> JobRun:
        job = JobRun(source=source, status="running")
        self.session.add(job)
        await self.session.commit()
        return job

    async def finish_job(
        self, job: JobRun, collected: int, saved: int, failures: int
    ) -> None:
        job.status = "completed"
        job.ended_at = datetime.now(timezone.utc)
        job.listings_collected = collected
        job.listings_saved = saved
        job.failures = failures
        job.success_rate = collected / (collected + failures) if collected + failures else 1
        await self.session.commit()

    async def fail_job(self, job: JobRun, error: Exception, failures: int) -> None:
        job.status = "failed"
        job.ended_at = datetime.now(timezone.utc)
        job.failures = failures
        job.error = str(error)
        self.session.add(
            CollectorLog(
                job_run_id=job.id,
                source=job.source,
                level="error",
                message=str(error),
            )
        )
        await self.session.commit()

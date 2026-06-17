import hashlib
import re

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ingestion import PropertyDuplicate
from app.models.property import Property
from ingestion.schema import Listing


class DeduplicationEngine:
    """Creates fingerprints and manages property duplicates."""

    def __init__(self, db: AsyncSession):
        self.db = db

    def generate_fingerprint(self, listing: Listing) -> str:
        """
        Generate a stable SHA256 fingerprint from canonical attributes.
        Uses a combination of normalized locality, price, area, and bedrooms.
        """
        # Normalize text to remove whitespace variations and special chars
        locality_norm = re.sub(r'[^a-z0-9]', '', str(listing.locality).lower())
        
        components = [
            locality_norm,
            str(listing.price),
            str(listing.area_sqft),
            str(listing.bedrooms or 0)
        ]
        
        raw_fingerprint = "|".join(components)
        return hashlib.sha256(raw_fingerprint.encode("utf-8")).hexdigest()

    async def check_duplicate(self, listing: Listing, fingerprint: str) -> str | None:
        """
        Checks if a listing already exists. 
        If it exists by source + external_id, we check for changes (e.g. price, status).
        If it doesn't exist, we check if the fingerprint matches an existing property from another source.
        """
        from app.models.events import PropertyEvent
        import datetime

        # 1. Look for exact match by source + external_id
        stmt = select(Property).where(
            Property.source == listing.source,
            Property.external_id == listing.external_id
        )
        result = await self.db.execute(stmt)
        existing_prop = result.scalar_one_or_none()

        if existing_prop:
            # Change Detection
            if existing_prop.price != listing.price:
                event = PropertyEvent(
                    property_id=existing_prop.id,
                    event_type="PRICE_CHANGED",
                    old_value={"price": existing_prop.price},
                    new_value={"price": listing.price},
                    source=listing.source
                )
                self.db.add(event)
                existing_prop.price = listing.price
                if listing.area_sqft > 0:
                    existing_prop.price_per_sqft = listing.price / listing.area_sqft

            # Note: We can add more change detections here (status, area)
            existing_prop.last_seen_at = datetime.datetime.utcnow()
            await self.db.commit()
            return existing_prop.id

        # 2. Check if the property already exists with this fingerprint (Duplicate across sources)
        stmt_fp = select(Property.id).where(Property.fingerprint == fingerprint)
        result_fp = await self.db.execute(stmt_fp)
        primary_id = result_fp.scalar_one_or_none()

        if primary_id:
            # Add to property_duplicates mapping
            duplicate_stmt = select(PropertyDuplicate).where(
                PropertyDuplicate.source == listing.source,
                PropertyDuplicate.external_id == listing.external_id
            )
            dup_result = await self.db.execute(duplicate_stmt)
            if not dup_result.scalar_one_or_none():
                dup_record = PropertyDuplicate(
                    source=listing.source,
                    external_id=listing.external_id,
                    property_id=primary_id,
                    fingerprint=fingerprint
                )
                self.db.add(dup_record)
                await self.db.commit()
            
            return primary_id

        return None

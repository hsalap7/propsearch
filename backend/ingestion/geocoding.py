from dataclasses import dataclass
from typing import Any

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.ingestion import GeocodeCache
from ingestion.schema import Listing, normalize_text


@dataclass
class GeocodeResult:
    latitude: float
    longitude: float
    provider: str
    raw_response: Any = None


class Geocoder:
    """Geocode with source coordinates, Google, then Nominatim; cache all results."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def geocode(self, listing: Listing) -> GeocodeResult | None:
        query = normalize_text(
            ", ".join(filter(None, [listing.address, listing.locality, listing.city]))
        )
        cached = await self.session.scalar(
            select(GeocodeCache).where(GeocodeCache.query == query)
        )
        if cached:
            return GeocodeResult(cached.latitude, cached.longitude, cached.provider)

        result = None
        if listing.latitude is not None and listing.longitude is not None:
            result = GeocodeResult(listing.latitude, listing.longitude, "source")
        result = result or await self._google(query) or await self._nominatim(query)
        if result:
            self.session.add(
                GeocodeCache(
                    query=query,
                    latitude=result.latitude,
                    longitude=result.longitude,
                    provider=result.provider,
                    raw_response=result.raw_response,
                )
            )
        return result

    async def _google(self, query: str) -> GeocodeResult | None:
        if not settings.google_geocoding_api_key:
            return None
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.get(
                "https://maps.googleapis.com/maps/api/geocode/json",
                params={"address": query, "key": settings.google_geocoding_api_key},
            )
            response.raise_for_status()
            payload = response.json()
        if not payload.get("results"):
            return None
        location = payload["results"][0]["geometry"]["location"]
        return GeocodeResult(location["lat"], location["lng"], "google", payload)

    async def _nominatim(self, query: str) -> GeocodeResult | None:
        async with httpx.AsyncClient(
            timeout=15, headers={"User-Agent": settings.nominatim_user_agent}
        ) as client:
            response = await client.get(
                "https://nominatim.openstreetmap.org/search",
                params={"q": query, "format": "jsonv2", "limit": 1},
            )
            response.raise_for_status()
            payload = response.json()
        if not payload:
            return None
        return GeocodeResult(
            float(payload[0]["lat"]), float(payload[0]["lon"]), "nominatim", payload
        )

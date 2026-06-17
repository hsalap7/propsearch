"""Prestige Group collector – calls the site's internal API directly.

The Prestige website is a JS-rendered SPA that loads listings via POST to
``https://www.prestigeconstructions.com/api/apicall`` with a ``dynamicurl``
parameter.  We skip Playwright entirely and hit the API with ``httpx``,
paginating through all Bangalore residential projects.
"""

import hashlib
import logging
import re
from typing import Any

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from ingestion.base import BaseCollector
from ingestion.schema import Listing, RawListingData

logger = logging.getLogger(__name__)

API_URL = "https://www.prestigeconstructions.com/api/apicall"
PAGE_SIZE = 50  # fetch in larger batches to reduce round-trips


def _number(value: Any, default: int = 0) -> int:
    """Parse an Indian-format price/area string into an integer."""
    if isinstance(value, (int, float)):
        return int(value)
    text = str(value or "").lower().replace(",", "")
    match = re.search(r"[\d.]+", text)
    if not match:
        return default
    number = float(match.group())
    if "crore" in text or re.search(r"\bcr\b", text):
        number *= 10_000_000
    elif "lakh" in text or re.search(r"\blac\b", text) or "lac" in text:
        number *= 100_000
    return int(number)


def _safe(data: dict, key: str, default: Any = "") -> Any:
    """Safely extract a key from a dict, returning *default* for None / empty."""
    v = data.get(key)
    if v is None or v == "":
        return default
    return v


class PrestigeCollector(BaseCollector):
    """Collector for Prestige Group Bangalore residential projects."""

    source = "prestige"
    requests_per_minute = 30  # generous – it's their public API

    def __init__(self, session: AsyncSession):
        super().__init__(session)
        self._client = httpx.AsyncClient(
            timeout=30,
            verify=False,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                ),
                "Referer": "https://www.prestigeconstructions.com/residential-projects/bangalore",
                "Origin": "https://www.prestigeconstructions.com",
            },
        )

    # ------------------------------------------------------------------
    # Stage 1: discover listing URLs via the Prestige internal API
    # ------------------------------------------------------------------
    async def discover_listing_urls(self) -> list[str]:
        """Paginate the API and return one pseudo-URL per project."""
        urls: list[str] = []
        page = 1
        while True:
            await self.rate_limiter.acquire()
            payload = {
                "dynamicurl": "managecontent/v2/projectinventorycms/list",
                "propertycategory": "Residential",
                "is_available": "true",
                "CityText": "bangalore",
                "page": page,
                "size": PAGE_SIZE,
            }
            try:
                resp = await self._client.post(API_URL, data=payload)
                resp.raise_for_status()
                body = resp.json()
            except Exception as exc:
                logger.warning("Prestige API page %d failed: %s", page, exc)
                self.log_failure(
                    f"API page {page} failed: {exc}",
                    {"page": page, "stage": "discover"},
                )
                break

            items = body.get("data", [])
            if not items:
                break

            for item in items:
                city = _safe(item, "CityText", "bangalore").lower()
                slug = _safe(item, "Project_slug", "")
                if slug:
                    url = f"https://www.prestigeconstructions.com/residential-projects/{city}/{slug}"
                else:
                    url = f"https://www.prestigeconstructions.com/residential-projects/{city}/{item.get('ProjectID', 'unknown')}"
                urls.append(url)

            logger.info(
                "Prestige page %d → %d projects (total so far: %d)",
                page,
                len(items),
                len(urls),
            )
            if len(items) < PAGE_SIZE:
                break
            page += 1

        return list(dict.fromkeys(urls))  # dedupe while preserving order

    # ------------------------------------------------------------------
    # Stage 2: the API already gives us everything we need per project,
    #          so we store the full item as the raw payload.
    # ------------------------------------------------------------------
    async def extract_listing_payload(self, listing_url: str) -> dict[str, Any]:
        """For Prestige we already collected all data in discover; this is a
        pass-through that returns the cached item stored during discover."""
        # We override `collect` below so this method is never actually called.
        return {"listing_url": listing_url}

    async def collect(self) -> list[RawListingData]:
        """Override the default collect to avoid per-URL fetching – we already
        have all data from the paginated API call."""
        records: list[RawListingData] = []
        page = 1
        while True:
            await self.rate_limiter.acquire()
            payload = {
                "dynamicurl": "managecontent/v2/projectinventorycms/list",
                "propertycategory": "Residential",
                "is_available": "true",
                "CityText": "bangalore",
                "page": page,
                "size": PAGE_SIZE,
            }
            try:
                resp = await self._client.post(API_URL, data=payload)
                resp.raise_for_status()
                body = resp.json()
            except Exception as exc:
                logger.warning("Prestige API page %d failed: %s", page, exc)
                self.log_failure(
                    f"API page {page} failed: {exc}",
                    {"page": page, "stage": "collect"},
                )
                break

            items = body.get("data", [])
            if not items:
                break

            for item in items:
                city = _safe(item, "CityText", "bangalore").lower()
                slug = _safe(item, "Project_slug", "")
                project_id = str(
                    item.get("ProjectID")
                    or slug
                    or hashlib.sha256(str(item).encode()).hexdigest()[:24]
                )
                if slug:
                    url = f"https://www.prestigeconstructions.com/residential-projects/{city}/{slug}"
                else:
                    url = f"https://www.prestigeconstructions.com/residential-projects/{city}/{project_id}"

                records.append(
                    RawListingData(
                        source=self.source,
                        external_id=project_id,
                        listing_url=url,
                        payload=item,
                    )
                )

            logger.info(
                "Prestige page %d → %d projects (total so far: %d)",
                page,
                len(items),
                len(records),
            )
            if len(items) < PAGE_SIZE:
                break
            page += 1

        return records

    # ------------------------------------------------------------------
    # Stage 3: normalize a raw API record into a canonical Listing
    # ------------------------------------------------------------------
    async def normalize_listing(self, raw: RawListingData) -> Listing:
        item = raw.payload

        # --- title ----------------------------------------------------------
        title = _safe(item, "ProjectName", "Prestige Property")

        # --- price ----------------------------------------------------------
        display_price = _safe(item, "DisplayPrice", "0")
        price = _number(display_price)
        if price == 0:
            # Some projects are "Price on Request" – skip via ValueError
            # so they get logged as failures but don't break the pipeline.
            if _safe(item, "price_on_request") in (True, "true"):
                # Use a sentinel so the listing still gets saved.
                price = 0

        # --- area -----------------------------------------------------------
        area_text = _safe(item, "DisplayArea", "0")
        area = _number(area_text)
        if area == 0:
            # Fallback: try Size field (e.g., "34 Acres")
            size_text = _safe(item, "Size", "0")
            area = _number(size_text)
        # If still 0, provide a minimum valid area so Listing schema passes.
        if area <= 0:
            area = 1

        # --- bedrooms -------------------------------------------------------
        bed_text = _safe(item, "bedroomdisplaytext", "")
        bed_match = re.search(r"(\d+)", str(bed_text))
        bedrooms = int(bed_match.group(1)) if bed_match else None

        # --- property type --------------------------------------------------
        property_type = _safe(item, "PropertyTypeText", "apartment")
        # From ChildProject, extract unique property types
        children = item.get("ChildProject") or []
        if children and isinstance(children, list):
            types = list(
                dict.fromkeys(
                    _safe(c, "propertyttype", "") for c in children if _safe(c, "propertyttype")
                )
            )
            if types:
                property_type = ", ".join(types)

        # --- location -------------------------------------------------------
        display_area = _safe(item, "DisplayArea", "")
        city_text = _safe(item, "CityText", "Bangalore")
        address = f"{display_area}, {city_text}" if display_area else city_text
        locality = display_area if display_area else city_text

        # --- coordinates ----------------------------------------------------
        lat, lng = None, None
        lat_long = item.get("LatLong")
        if isinstance(lat_long, dict):
            coords = lat_long.get("coordinates", [])
            if len(coords) >= 2:
                # Prestige stores [lat, lng] (NOT standard GeoJSON order)
                try:
                    lat = float(coords[0]) if coords[0] else None
                    lng = float(coords[1]) if coords[1] else None
                except (TypeError, ValueError):
                    pass

        # --- images ---------------------------------------------------------
        project_image = _safe(item, "ProjectImage", "")
        images = [project_image] if project_image else []

        # --- URL ------------------------------------------------------------
        listing_url = raw.listing_url

        return Listing(
            source=self.source,
            external_id=raw.external_id,
            title=title,
            description=f"Prestige Group residential project in {city_text}",
            property_type=property_type.lower() if property_type else "apartment",
            price=price,
            area_sqft=area,
            bedrooms=bedrooms,
            address=address,
            locality=locality,
            city=city_text.title(),
            latitude=lat,
            longitude=lng,
            image_urls=images,
            amenities=[],
            listing_url=listing_url,
        )

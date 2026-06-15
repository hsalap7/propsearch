"""Playwright-first collector helpers for real-estate portals."""

import json
import re
from html import unescape
from typing import Any

from ingestion.base import BaseCollector
from ingestion.schema import Listing, RawListingData


def _number(value: Any, default: int = 0) -> int:
    if isinstance(value, (int, float)):
        return int(value)
    text = str(value or "").lower().replace(",", "")
    match = re.search(r"[\d.]+", text)
    if not match:
        return default
    number = float(match.group())
    if "crore" in text or re.search(r"\bcr\b", text):
        number *= 10_000_000
    elif "lakh" in text or re.search(r"\blac\b", text):
        number *= 100_000
    return int(number)


def _first(payload: dict[str, Any], *keys: str, default: Any = None) -> Any:
    for key in keys:
        value: Any = payload
        for part in key.split("."):
            if not isinstance(value, dict):
                value = None
                break
            value = value.get(part)
        if value not in (None, "", [], {}):
            return value
    return default


class PortalCollector(BaseCollector):
    """Configurable portal adapter using links and JSON-LD as stable fallbacks."""

    search_urls: list[str] = []
    listing_url_pattern: str = ""

    async def _page_content(self, url: str) -> tuple[str, str]:
        try:
            from playwright.async_api import async_playwright
        except ImportError as exc:
            raise RuntimeError(
                "Playwright is required; install dependencies and run "
                "`playwright install chromium`."
            ) from exc

        from app.core.config import settings

        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(headless=settings.collector_headless)
            page = await browser.new_page()
            await page.goto(url, wait_until="domcontentloaded", timeout=45_000)
            await page.wait_for_timeout(1_000)
            content, final_url = await page.content(), page.url
            await browser.close()
            return content, final_url

    async def discover_listing_urls(self) -> list[str]:
        urls: list[str] = []
        pattern = re.compile(self.listing_url_pattern)
        for search_url in self.search_urls:
            html, _ = await self._page_content(search_url)
            for href in re.findall(r'href=["\']([^"\']+)', html):
                if pattern.search(href):
                    if href.startswith("/"):
                        origin = re.match(r"https?://[^/]+", search_url)
                        href = f"{origin.group()}{href}" if origin else href
                    urls.append(unescape(href))
        return list(dict.fromkeys(urls))

    async def extract_listing_payload(self, listing_url: str) -> dict[str, Any]:
        html, final_url = await self._page_content(listing_url)
        json_ld = []
        for value in re.findall(
            r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
            html,
            flags=re.DOTALL | re.IGNORECASE,
        ):
            try:
                json_ld.append(json.loads(value))
            except json.JSONDecodeError:
                continue
        return {"listing_url": final_url, "json_ld": json_ld, "html": html}

    async def normalize_listing(self, raw: RawListingData) -> Listing:
        payload = self._structured_payload(raw.payload)
        address = _first(payload, "address.streetAddress", "address", "location", default="")
        locality = _first(
            payload,
            "address.addressLocality",
            "locality",
            "neighborhood",
            default="",
        )
        city = _first(payload, "address.addressRegion", "city", default="Bangalore")
        images = _first(payload, "image", "images", default=[])
        if isinstance(images, str):
            images = [images]
        amenities = _first(payload, "amenities", "amenityFeature", default=[])
        amenities = [
            item.get("name", "") if isinstance(item, dict) else str(item)
            for item in amenities
        ]
        price = _number(_first(payload, "offers.price", "price", "price.value"))
        area = _number(
            _first(
                payload,
                "floorSize.value",
                "area_sqft",
                "area",
                "builtUpArea",
            )
        )
        if not address or not price or not area:
            raise ValueError("Source payload is missing address, price, or area")
        return Listing(
            source=self.source,
            external_id=raw.external_id,
            title=str(_first(payload, "name", "title", default="Property listing")),
            description=str(_first(payload, "description", default="")),
            property_type=str(_first(payload, "@type", "property_type", default="residential")),
            price=price,
            area_sqft=area,
            bedrooms=_number(_first(payload, "numberOfRooms", "bedrooms"), default=0)
            or None,
            bathrooms=_number(_first(payload, "numberOfBathroomsTotal", "bathrooms"), default=0)
            or None,
            address=str(address),
            locality=str(locality),
            city=str(city),
            latitude=self._optional_float(_first(payload, "geo.latitude", "latitude")),
            longitude=self._optional_float(_first(payload, "geo.longitude", "longitude")),
            image_urls=images,
            amenities=[value for value in amenities if value],
            listing_url=raw.listing_url,
        )

    @staticmethod
    def _structured_payload(payload: dict[str, Any]) -> dict[str, Any]:
        candidates = payload.get("json_ld", [])
        for candidate in candidates:
            if isinstance(candidate, list):
                candidate = candidate[0] if candidate else {}
            if isinstance(candidate, dict) and candidate.get("@graph"):
                candidate = candidate["@graph"][0]
            if isinstance(candidate, dict) and (
                candidate.get("offers") or candidate.get("floorSize")
            ):
                return candidate
        return payload

    @staticmethod
    def _optional_float(value: Any) -> float | None:
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

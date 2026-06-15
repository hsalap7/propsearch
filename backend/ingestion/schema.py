import hashlib
import re
from datetime import datetime, timezone
from typing import Any
from urllib.parse import urlparse

from pydantic import BaseModel, Field, field_validator


def normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip().lower())


class RawListingData(BaseModel):
    source: str
    external_id: str
    listing_url: str
    payload: dict[str, Any]

    @classmethod
    def from_payload(
        cls, source: str, listing_url: str, payload: dict[str, Any]
    ) -> "RawListingData":
        external_id = str(
            payload.get("external_id")
            or payload.get("id")
            or hashlib.sha256(listing_url.encode()).hexdigest()[:24]
        )
        return cls(
            source=source,
            external_id=external_id,
            listing_url=listing_url,
            payload=payload,
        )


class Listing(BaseModel):
    source: str
    external_id: str
    title: str
    description: str = ""
    property_type: str = "residential"
    price: int = Field(ge=0)
    area_sqft: int = Field(gt=0)
    bedrooms: int | None = Field(default=None, ge=0)
    bathrooms: int | None = Field(default=None, ge=0)
    address: str
    locality: str
    city: str
    latitude: float | None = None
    longitude: float | None = None
    image_urls: list[str] = Field(default_factory=list)
    amenities: list[str] = Field(default_factory=list)
    listing_url: str
    last_seen_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("image_urls")
    @classmethod
    def only_http_images(cls, values: list[str]) -> list[str]:
        return list(
            dict.fromkeys(
                value
                for value in values
                if urlparse(value).scheme in {"http", "https"}
            )
        )

    @property
    def fingerprint(self) -> str:
        value = f"{normalize_text(self.address)}{self.area_sqft}{self.price}"
        return hashlib.sha256(value.encode()).hexdigest()

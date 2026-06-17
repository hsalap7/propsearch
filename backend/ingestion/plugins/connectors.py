import csv
import io
import json
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from openpyxl import load_workbook

from app.models.ingestion import RawPayload
from ingestion.core.session import SessionManager
from ingestion.schema import Listing


class JSONPlugin:
    source_name = "json_upload"

    def __init__(self, db: AsyncSession, session_manager: SessionManager):
        self.db = db
        self.session_manager = session_manager

    def normalize(self, payload: RawPayload) -> list[Listing]:
        listings = []
        data = payload.payload_json
        if isinstance(data, dict) and "data" in data:
            data = data["data"]
        elif not isinstance(data, list):
            data = [data]
            
        for item in data:
            listings.append(
                Listing(
                    source=self.source_name,
                    external_id=str(item.get("id", item.get("external_id"))),
                    title=item.get("title", ""),
                    property_type=item.get("property_type", "apartment"),
                    price=item.get("price", 0),
                    area_sqft=item.get("area_sqft", 0),
                    bedrooms=item.get("bedrooms"),
                    address=item.get("address", ""),
                    locality=item.get("locality", ""),
                    city=item.get("city", "Bangalore"),
                    latitude=item.get("latitude"),
                    longitude=item.get("longitude"),
                    listing_url=item.get("url", f"https://local/{self.source_name}/{item.get('id')}"),
                )
            )
        return listings


class CSVPlugin:
    source_name = "csv_upload"

    def __init__(self, db: AsyncSession, session_manager: SessionManager):
        self.db = db

    def normalize(self, payload: RawPayload) -> list[Listing]:
        listings = []
        # payload_json contains parsed rows from the ingest API
        rows = payload.payload_json.get("rows", [])
        for i, row in enumerate(rows):
            listings.append(
                Listing(
                    source=self.source_name,
                    external_id=row.get("id", str(i)),
                    title=row.get("title", "CSV Uploaded Property"),
                    property_type=row.get("property_type", "apartment"),
                    price=int(float(row.get("price", 0))),
                    area_sqft=int(float(row.get("area_sqft", 0))),
                    bedrooms=int(float(row.get("bedrooms", 0))) if row.get("bedrooms") else None,
                    address=row.get("address", ""),
                    locality=row.get("locality", ""),
                    city=row.get("city", "Bangalore"),
                    latitude=float(row.get("latitude")) if row.get("latitude") else None,
                    longitude=float(row.get("longitude")) if row.get("longitude") else None,
                    listing_url=f"https://local/{self.source_name}/{row.get('id', i)}",
                )
            )
        return listings


class ExcelPlugin(CSVPlugin):
    """Excel plugin uses the exact same structure as CSV since the ingest API parses it."""
    source_name = "excel_upload"


class BuilderWebsitePlugin:
    source_name = "builder_direct"

    def __init__(self, db: AsyncSession, session_manager: SessionManager):
        self.db = db
        self.session_manager = session_manager

    def normalize(self, payload: RawPayload) -> list[Listing]:
        # Implementation for a specific builder logic
        # e.g., mapping fields from a Prestige or Godrej API JSON response
        listings = []
        for item in payload.payload_json.get("projects", []):
            listings.append(
                Listing(
                    source=self.source_name,
                    external_id=item.get("project_id"),
                    title=item.get("name"),
                    property_type="apartment",
                    price=item.get("starting_price", 0),
                    area_sqft=item.get("carpet_area", 0),
                    address=item.get("location_name", ""),
                    locality=item.get("location_name", ""),
                    city="Bangalore",
                    latitude=item.get("lat"),
                    longitude=item.get("lng"),
                    listing_url=item.get("website_url"),
                )
            )
        return listings


class ManualUploadPlugin:
    source_name = "manual_upload"

    def __init__(self, db: AsyncSession, session_manager: SessionManager):
        self.db = db

    def normalize(self, payload: RawPayload) -> list[Listing]:
        data = payload.payload_json
        return [
            Listing(
                source=self.source_name,
                external_id=str(data.get("id", data.get("external_id"))),
                title=data.get("title", "Broker Uploaded Property"),
                property_type=data.get("property_type", "apartment"),
                price=data.get("price", 0),
                area_sqft=data.get("area_sqft", 0),
                address=data.get("address", ""),
                locality=data.get("locality", ""),
                city=data.get("city", "Bangalore"),
                latitude=data.get("lat", data.get("latitude")),
                longitude=data.get("lng", data.get("longitude")),
                listing_url=data.get("url", f"https://local/manual/{data.get('id')}"),
            )
        ]

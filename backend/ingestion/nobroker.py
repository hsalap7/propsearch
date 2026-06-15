"""NoBroker data source adapter.

Framework for collecting and normalizing data from NoBroker.
"""

from typing import Any
from ingestion.base import DataSource


class NoBrokerSource(DataSource):
    """NoBroker data source.
    
    Note: Currently returns mock data. Real implementation would require
    web scraping or API integration with nobroker.com.
    """

    async def collect(self) -> list[dict[str, Any]]:
        """Collect properties from NoBroker (mock data)."""
        # TODO: Implement actual NoBroker API/scraping
        return []

    async def normalize(self, raw_data: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Normalize NoBroker data to standard schema."""
        # TODO: Implement normalization logic
        return []

    async def save(self, normalized_data: list[dict[str, Any]]) -> int:
        """Save properties to database."""
        # TODO: Implement database save logic
        return 0

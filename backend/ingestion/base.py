"""Data ingestion framework.

Base classes for implementing property data sources.
"""

from abc import ABC, abstractmethod
from typing import Any


class DataSource(ABC):
    """Abstract base class for data sources."""

    @abstractmethod
    async def collect(self) -> list[dict[str, Any]]:
        """Collect raw data from the source.
        
        Returns:
            List of raw property data dictionaries.
        """
        pass

    @abstractmethod
    async def normalize(self, raw_data: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Normalize raw data to standard schema.
        
        Args:
            raw_data: List of raw property data.
            
        Returns:
            List of normalized property data.
        """
        pass

    @abstractmethod
    async def save(self, normalized_data: list[dict[str, Any]]) -> int:
        """Save normalized data to database.
        
        Args:
            normalized_data: List of normalized property data.
            
        Returns:
            Number of properties saved.
        """
        pass

    async def ingest(self) -> int:
        """Execute full ingestion pipeline.
        
        Returns:
            Number of properties ingested.
        """
        raw_data = await self.collect()
        normalized_data = await self.normalize(raw_data)
        count = await self.save(normalized_data)
        return count

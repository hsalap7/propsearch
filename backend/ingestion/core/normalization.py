from typing import Any, Protocol

from app.models.ingestion import RawPayload
from ingestion.schema import Listing


class NormalizerPlugin(Protocol):
    """Protocol for source-specific normalizers."""
    def normalize(self, raw: RawPayload) -> list[Listing]:
        ...


class NormalizationEngine:
    """Converts source-specific payloads into canonical Property/Listing models."""

    def __init__(self, normalizer: NormalizerPlugin):
        self.normalizer = normalizer

    def process_payload(self, payload: RawPayload) -> list[Listing]:
        """
        Takes a raw JSON payload and returns canonical Listing models
        using the provided source-specific normalizer plugin.
        """
        try:
            return self.normalizer.normalize(payload)
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Failed to normalize payload {payload.id}: {e}")
            return []

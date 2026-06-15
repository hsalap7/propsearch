"""Shared collector contract and resilient collection workflow."""

import asyncio
import time
from abc import ABC, abstractmethod
from collections.abc import Awaitable, Callable
from typing import Any, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ingestion import CollectorLog
from ingestion.schema import Listing, RawListingData
from ingestion.service import IngestionService

T = TypeVar("T")


class TokenBucket:
    """Small async token bucket used to enforce per-source request limits."""

    def __init__(self, requests_per_minute: int):
        self.capacity = max(requests_per_minute, 1)
        self.tokens = float(self.capacity)
        self.refill_rate = self.capacity / 60
        self.updated_at = time.monotonic()
        self._lock = asyncio.Lock()

    async def acquire(self) -> None:
        while True:
            async with self._lock:
                now = time.monotonic()
                self.tokens = min(
                    self.capacity,
                    self.tokens + (now - self.updated_at) * self.refill_rate,
                )
                self.updated_at = now
                if self.tokens >= 1:
                    self.tokens -= 1
                    return
                delay = (1 - self.tokens) / self.refill_rate
            await asyncio.sleep(delay)


async def with_backoff(
    operation: Callable[[], Awaitable[T]], max_retries: int = 5
) -> T:
    """Run an async operation with 1, 2, 4, 8... second backoff."""
    for attempt in range(max_retries + 1):
        try:
            return await operation()
        except Exception:
            if attempt == max_retries:
                raise
            await asyncio.sleep(2**attempt)
    raise RuntimeError("unreachable")


class BaseCollector(ABC):
    """Every source emits raw records and canonical listings through this contract."""

    source: str
    requests_per_minute: int = 20

    def __init__(self, session: AsyncSession):
        self.session = session
        self.rate_limiter = TokenBucket(self.requests_per_minute)
        self.failures = 0
        self.job_run_id: str | None = None

    def log_failure(self, message: str, context: dict[str, Any]) -> None:
        self.failures += 1
        self.session.add(
            CollectorLog(
                job_run_id=self.job_run_id,
                source=self.source,
                level="error",
                message=message,
                context=context,
            )
        )

    @abstractmethod
    async def discover_listing_urls(self) -> list[str]:
        """Stage 1: collect listing URLs."""

    @abstractmethod
    async def extract_listing_payload(self, listing_url: str) -> dict[str, Any]:
        """Stage 2: extract the original source payload for one detail page."""

    @abstractmethod
    async def normalize_listing(self, raw: RawListingData) -> Listing:
        """Stage 3: convert one raw record into the canonical schema."""

    async def collect(self) -> list[RawListingData]:
        records: list[RawListingData] = []
        for listing_url in await self.discover_listing_urls():
            try:
                await self.rate_limiter.acquire()
                payload = await with_backoff(
                    lambda url=listing_url: self.extract_listing_payload(url)
                )
                records.append(
                    RawListingData.from_payload(self.source, listing_url, payload)
                )
            except Exception as exc:
                self.log_failure(str(exc), {"listing_url": listing_url, "stage": "collect"})
        return records

    async def normalize(self, raw_data: list[RawListingData]) -> list[Listing]:
        listings: list[Listing] = []
        for raw in raw_data:
            try:
                listings.append(await self.normalize_listing(raw))
            except Exception as exc:
                self.log_failure(
                    str(exc),
                    {
                        "external_id": raw.external_id,
                        "listing_url": raw.listing_url,
                        "stage": "normalize",
                    },
                )
        return listings

    async def save(
        self, normalized_data: list[Listing], raw_data: list[RawListingData] | None = None
    ) -> int:
        return await IngestionService(self.session).save(
            normalized_data, raw_data or []
        )

    async def ingest(self) -> int:
        """Execute collection while always persisting original payloads first."""
        service = IngestionService(self.session)
        job = await service.start_job(self.source)
        self.job_run_id = job.id
        try:
            raw_data = await self.collect()
            await service.save_raw(raw_data)
            normalized_data = await self.normalize(raw_data)
            saved = await service.save(normalized_data)
            await service.finish_job(
                job,
                collected=len(raw_data),
                saved=saved,
                failures=self.failures,
            )
            return saved
        except Exception as exc:
            await service.fail_job(job, exc, self.failures + 1)
            raise

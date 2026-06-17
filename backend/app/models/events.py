from datetime import datetime
from typing import Any, Optional
from uuid import uuid4

from sqlalchemy import JSON, TIMESTAMP, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base
from app.models.ingestion import JSON_TYPE


class PropertyEvent(Base):
    """Tracks changes to properties over time."""

    __tablename__ = "property_events"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid4())
    )
    property_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("properties.id", ondelete="CASCADE"), nullable=False, index=True
    )
    event_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    old_value: Mapped[Optional[Any]] = mapped_column(JSON_TYPE, nullable=True)
    new_value: Mapped[Optional[Any]] = mapped_column(JSON_TYPE, nullable=True)
    source: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, nullable=False, server_default=func.now(), index=True
    )

    def __repr__(self) -> str:
        return f"<PropertyEvent(property_id={self.property_id}, type={self.event_type})>"

from datetime import datetime
from typing import Optional
from uuid import uuid4

from sqlalchemy import JSON, TIMESTAMP, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base
from app.models.ingestion import JSON_TYPE


class SourceSession(Base):
    __tablename__ = "source_sessions"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid4())
    )
    source: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    cookies: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Encrypted
    local_storage: Mapped[Optional[dict]] = mapped_column(JSON_TYPE, nullable=True)
    session_state: Mapped[Optional[dict]] = mapped_column(JSON_TYPE, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now()
    )

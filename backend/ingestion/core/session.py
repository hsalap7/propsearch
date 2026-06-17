import json
import logging
from typing import Any, Optional

from cryptography.fernet import Fernet
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.session import SourceSession

logger = logging.getLogger(__name__)


class CookieVault:
    def __init__(self):
        # We need a 32-byte url-safe base64-encoded key. 
        # If settings.secret_key is not 32 bytes base64, we derive one.
        key = settings.secret_key.encode("utf-8")
        if len(key) < 32:
            key = key.ljust(32, b"0")
        elif len(key) > 32:
            key = key[:32]
        import base64
        b64_key = base64.urlsafe_b64encode(key)
        self.fernet = Fernet(b64_key)

    def encrypt(self, data: str) -> str:
        return self.fernet.encrypt(data.encode()).decode()

    def decrypt(self, token: str) -> str:
        return self.fernet.decrypt(token.encode()).decode()


class SessionManager:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.vault = CookieVault()

    async def save_session(
        self,
        source: str,
        cookies: Optional[list[dict[str, Any]]] = None,
        local_storage: Optional[dict[str, Any]] = None,
        session_state: Optional[dict[str, Any]] = None,
    ) -> None:
        """Save or update a session for a given source."""
        stmt = select(SourceSession).where(SourceSession.source == source)
        result = await self.db.execute(stmt)
        session_record = result.scalar_one_or_none()

        encrypted_cookies = None
        if cookies is not None:
            encrypted_cookies = self.vault.encrypt(json.dumps(cookies))

        if session_record:
            if cookies is not None:
                session_record.cookies = encrypted_cookies
            if local_storage is not None:
                session_record.local_storage = local_storage
            if session_state is not None:
                session_record.session_state = session_state
        else:
            session_record = SourceSession(
                source=source,
                cookies=encrypted_cookies,
                local_storage=local_storage,
                session_state=session_state,
            )
            self.db.add(session_record)

        await self.db.commit()
        logger.info(f"Saved session state for source: {source}")

    async def load_session(
        self, source: str
    ) -> tuple[Optional[list[dict[str, Any]]], Optional[dict[str, Any]], Optional[dict[str, Any]]]:
        """Load session data for a given source."""
        stmt = select(SourceSession).where(SourceSession.source == source)
        result = await self.db.execute(stmt)
        session_record = result.scalar_one_or_none()

        if not session_record:
            return None, None, None

        cookies = None
        if session_record.cookies:
            try:
                decrypted = self.vault.decrypt(session_record.cookies)
                cookies = json.loads(decrypted)
            except Exception as e:
                logger.warning(f"Failed to decrypt cookies for {source}: {e}")

        return cookies, session_record.local_storage, session_record.session_state

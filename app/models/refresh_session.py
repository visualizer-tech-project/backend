from datetime import datetime, timezone

from sqlalchemy import TIMESTAMP, Column
from sqlmodel import Field, Index

from app.models.base import BaseSQLModel


class RefreshSession(BaseSQLModel, table=True):
    __tablename__ = 'refresh_sessions'
    __table_args__ = (
        Index('ix_refresh_sessions_user_id', 'user_id'),
        Index('ix_refresh_sessions_is_valid', 'is_valid'),
    )

    user_id: int = Field(foreign_key='users.id', nullable=False)
    jti: str = Field(max_length=255, unique=True, nullable=False, index=True)
    expires_at: datetime = Field(
        default=None,
        sa_column=Column(TIMESTAMP(timezone=True), nullable=False)
    )
    is_valid: bool = Field(default=True, nullable=False)

    def is_expired(self) -> bool:
        expires_at = self.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        return datetime.now(timezone.utc) > expires_at

    def invalidate(self) -> None:
        self.is_valid = False

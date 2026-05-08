import uuid
from datetime import datetime, timezone, timedelta
from enum import Enum
from typing import TYPE_CHECKING

from sqlmodel import Field, Column, Relationship
from sqlalchemy import TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID

from app.models.base import BaseSQLModel
from app.core.settings import settings

if TYPE_CHECKING:
    from app.models.user import User


class EmailAction(int, Enum):
    VERIFY_ACCOUNT = 0
    CHANGE_PASSWORD = 1


class EmailNotification(BaseSQLModel, table=True):
    __tablename__ = 'email_notifications'

    code: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        sa_column=Column(UUID(as_uuid=True), unique=True, nullable=False, index=True),
    )
    user_id: int = Field(foreign_key='users.id', nullable=False, index=True)
    action: EmailAction = Field(nullable=False)
    expired_at: datetime = Field(
        default_factory=lambda: (
            datetime.now(timezone.utc)
            + timedelta(seconds=settings.email.notification_lifetime_seconds)
        ),
        sa_column=Column(TIMESTAMP(timezone=True), nullable=False),
    )
    is_used: bool = Field(default=False, nullable=False)

    user: 'User' = Relationship(back_populates='email_notifications')

    @property
    def is_expired(self) -> bool:
        return datetime.now(timezone.utc) > self.expired_at

    @property
    def is_valid(self) -> bool:
        return not self.is_used and not self.is_expired
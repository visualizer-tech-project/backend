import uuid
from typing import Optional

from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.email import EmailNotification, EmailAction
from app.repositories.base import BaseRepository


class EmailRepository(BaseRepository[EmailNotification, None, None]):
    def __init__(self, session: AsyncSession):
        super().__init__(EmailNotification, session)

    async def create_notification(
        self,
        user_id: int,
        action: EmailAction,
    ) -> EmailNotification:
        notification = EmailNotification(
            user_id=user_id,
            action=action,
        )
        return await self.save(notification)

    async def get_by_code(self, code: uuid.UUID) -> Optional[EmailNotification]:
        filters = self._create_filter_conditions_from_dict({'code': code})
        items, _ = await self.get_all(filters=filters, limit=1)
        return items[0] if items else None

    async def get_by_user_and_code(
        self,
        user_id: int,
        code: uuid.UUID,
    ) -> Optional[EmailNotification]:
        filters = self._create_filter_conditions_from_dict({
            'user_id': user_id,
            'code': code,
        })
        items, _ = await self.get_all(filters=filters, limit=1)
        return items[0] if items else None

    async def mark_as_used(self, notification: EmailNotification) -> EmailNotification:
        notification.is_used = True
        return await self.save(notification)
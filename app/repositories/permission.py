from typing import Optional

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.permission import Permission, PermissionCreate, PermissionUpdate
from app.repositories.base import BaseRepository


class PermissionRepository(BaseRepository[Permission, PermissionCreate, PermissionUpdate]):
    def __init__(self, session: AsyncSession):
        super().__init__(Permission, session)

    def _setup_filters(self):
        self.add_filter('subject')
        self.add_filter('action')

    async def get_by_subject_and_action(self, subject: str, action: str) -> Optional[Permission]:

        query = select(Permission).where(
            Permission.subject == subject,
            Permission.action == action
        )
        result = await self.session.exec(query)
        return result.first()

    async def get_or_create(self, subject: str, action: str) -> Permission:
        existing = await self.get_by_subject_and_action(subject, action)
        if existing:
            return existing

        permission_data = PermissionCreate(subject=subject, action=action)
        return await self.create(permission_data)
from typing import Optional

from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.permission import Permission, PermissionCreate, PermissionUpdate
from app.repositories.base import BaseRepository, FilterCondition


class PermissionRepository(BaseRepository[Permission, PermissionCreate, PermissionUpdate]):
    def __init__(self, session: AsyncSession):
        super().__init__(Permission, session)

    def _setup_filters(self):
        self.add_filter('subject')
        self.add_filter('action')

    async def get_by_subject_and_action(self, subject: str, action: str) -> Optional[Permission]:
        filters = [
            FilterCondition('subject', subject),
            FilterCondition('action', action)
        ]
        items, _ = await self.get_all(
            limit=1,
            filters=filters
        )
        return items[0] if items else None

    async def get_or_create(self, subject: str, action: str) -> Permission:
        existing = await self.get_by_subject_and_action(subject, action)
        if existing:
            return existing

        permission_data = PermissionCreate(subject=subject, action=action)
        return await self.create(permission_data)
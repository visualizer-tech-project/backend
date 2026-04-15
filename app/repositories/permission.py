import uuid
from typing import Optional, Sequence

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.permission import Permission, PermissionCreate, PermissionUpdate


class PermissionRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, permission: Permission) -> Permission:
        self.session.add(permission)
        await self.session.commit()
        await self.session.refresh(permission)
        return permission

    async def get_by_id(self, permission_id: uuid.UUID) -> Optional[Permission]:
        return await self.session.get(Permission, permission_id)

    async def get_by_subject_and_action(self, subject: str, action: str) -> Optional[Permission]:
        query = select(Permission).where(
            Permission.subject == subject,
            Permission.action == action
        )
        result = await self.session.exec(query)
        return result.first()

    async def get_all(self) -> Sequence[Permission]:
        query = select(Permission)
        result = await self.session.exec(query)
        return result.all()

    async def get_or_create(self, subject: str, action: str) -> Permission:
        existing = await self.get_by_subject_and_action(subject, action)
        if existing:
            return existing
        permission = Permission(subject=subject, action=action)
        return await self.save(permission)

    async def create(self, permission_data: PermissionCreate) -> Permission:
        permission = Permission(**permission_data.model_dump())
        return await self.save(permission)

    async def delete(self, permission_id: uuid.UUID) -> bool:
        permission = await self.get_by_id(permission_id)
        if not permission:
            return False
        await self.session.delete(permission)
        await self.session.commit()
        return True
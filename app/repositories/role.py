from typing import List, Optional, Sequence

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.role import Role, RoleCreate, RoleUpdate, UserRoleMapping
from app.models.permission import RolePermissionMapping
from app.repositories.base import BaseRepository


class RoleRepository(BaseRepository[Role, RoleCreate, RoleUpdate]):
    def __init__(self, session: AsyncSession):
        super().__init__(Role, session)

    def _setup_filters(self):
        self.add_filter('name')

    async def get_by_name(self, name: str) -> Optional[Role]:
        query = select(Role).where(Role.name == name)
        result = await self.session.exec(query)
        return result.first()

    async def get_with_permissions(self, role_id: int) -> Optional[Role]:
        role = await self.get_by_id(role_id)
        if role:
            await self.session.refresh(role, ['permissions'])
        return role

    async def get_user_roles(self, user_id: int) -> Sequence[Role]:
        query = (
            select(Role)
            .join(UserRoleMapping, UserRoleMapping.role_id == Role.id)
            .where(UserRoleMapping.user_id == user_id)
        )
        result = await self.session.exec(query)
        return result.all()

    async def get_or_create(self, name: str, description: Optional[str] = None) -> Role:
        existing = await self.get_by_name(name)
        if existing:
            return existing

        role_data = RoleCreate(name=name, description=description, scope_aliases=[])
        return await self.create(role_data)
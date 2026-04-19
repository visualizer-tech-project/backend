from typing import List, Optional, Sequence
from sqlmodel import delete, select
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
        filters = self._create_filter_conditions_from_dict({'name': name})
        items, _ = await self.get_all(filters=filters, limit=1)
        return items[0] if items else None

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

    async def set_role_permissions(self, role_id: int, permission_ids: List[int]) -> None:
        await self.session.exec(
            delete(RolePermissionMapping).where(RolePermissionMapping.role_id == role_id)
        )
        for perm_id in permission_ids:
            mapping = RolePermissionMapping(role_id=role_id, permission_id=perm_id)
            self.session.add(mapping)
        await self.session.commit()

    async def assign_roles_to_user(self, user_id: int, role_ids: List[int]) -> None:
        await self.session.exec(
            delete(UserRoleMapping).where(UserRoleMapping.user_id == user_id)
        )
        for role_id in role_ids:
            mapping = UserRoleMapping(user_id=user_id, role_id=role_id)
            self.session.add(mapping)
        await self.session.commit()

    async def get_role_with_permissions(self, role_id: int) -> Optional[Role]:
        role = await self.get_by_id(role_id)
        if role:
            await self.session.refresh(role, ['permissions'])
        return role

    async def get_role_by_name_with_permissions(self, name: str) -> Optional[Role]:
        role = await self.get_by_name(name)
        if role:
            await self.session.refresh(role, ['permissions'])
        return role

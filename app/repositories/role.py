import uuid
from typing import List, Optional, Sequence

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.role import Role, RoleCreate, RoleUpdate, UserRoleMapping
from app.models.permission import Permission, RolePermissionMapping


class RoleRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, role: Role) -> Role:
        self.session.add(role)
        await self.session.commit()
        await self.session.refresh(role)
        return role

    async def get_by_id(self, role_id: uuid.UUID) -> Optional[Role]:
        return await self.session.get(Role, role_id)

    async def get_by_name(self, name: str) -> Optional[Role]:
        query = select(Role).where(Role.name == name)
        result = await self.session.exec(query)
        return result.first()

    async def get_all(self) -> Sequence[Role]:
        query = select(Role)
        result = await self.session.exec(query)
        return result.all()

    async def get_with_permissions(self, role_id: uuid.UUID) -> Optional[Role]:
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

    async def create(self, role_data: RoleCreate) -> Role:
        role = Role(
            name=role_data.name,
            description=role_data.description,
        )
        return await self.save(role)

    async def update(self, role_id: uuid.UUID, role_data: RoleUpdate) -> Optional[Role]:
        role = await self.get_by_id(role_id)
        if not role:
            return None

        update_dict = role_data.model_dump(exclude_unset=True, exclude={'scope_aliases'})
        for field, value in update_dict.items():
            setattr(role, field, value)

        return await self.save(role)

    async def delete(self, role_id: uuid.UUID) -> bool:
        role = await self.get_by_id(role_id)
        if not role:
            return False
        await self.session.delete(role)
        await self.session.commit()
        return True

    async def set_permissions(self, role_id: uuid.UUID, permission_ids: List[uuid.UUID]) -> None:
        existing = await self.session.exec(
            select(RolePermissionMapping).where(RolePermissionMapping.role_id == role_id)
        )
        for mapping in existing:
            await self.session.delete(mapping)

        for perm_id in permission_ids:
            mapping = RolePermissionMapping(role_id=role_id, permission_id=perm_id)
            self.session.add(mapping)

        await self.session.commit()

    async def assign_roles_to_user(self, user_id: int, role_ids: List[uuid.UUID]) -> None:
        existing = await self.session.exec(
            select(UserRoleMapping).where(UserRoleMapping.user_id == user_id)
        )
        for mapping in existing:
            await self.session.delete(mapping)

        for role_id in role_ids:
            mapping = UserRoleMapping(user_id=user_id, role_id=role_id)
            self.session.add(mapping)

        await self.session.commit()

    async def get_or_create(self, name: str, description: Optional[str] = None) -> Role:
        existing = await self.get_by_name(name)
        if existing:
            return existing
        role = Role(name=name, description=description)
        return await self.save(role)
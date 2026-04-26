from typing import List, Optional

from app.core import exceptions
from app.models.user import User, UserRole
from app.models.role import Role, RoleCreate, RoleUpdate
from app.repositories.role import RoleRepository
from app.repositories.permission import PermissionRepository


class RoleService:
    def __init__(
            self,
            role_repository: RoleRepository,
            permission_repository: PermissionRepository,
    ):
        self._role_repository = role_repository
        self._permission_repository = permission_repository

    async def _parse_scope_aliases(self, scope_aliases: List[str]) -> List[int]:
        permission_ids = []
        for alias in scope_aliases:
            parts = alias.split(':', 1)
            if len(parts) == 2:
                subject, action = parts
                perm = await self._permission_repository.get_or_create(subject, action)
                permission_ids.append(perm.id)
        return permission_ids

    async def get_roles(self) -> List[Role]:
        roles, _ = await self._role_repository.get_all()
        return roles

    async def get_role_by_id(self, role_id: int) -> Role:
        role = await self._role_repository.get_with_permissions(role_id)
        if not role:
            raise exceptions.NotFoundError(f"Role with id {role_id} not found")
        return role

    async def get_role_by_name(self, name: str) -> Optional[Role]:
        return await self._role_repository.get_role_by_name_with_permissions(name)

    async def create_role(self, role_data: RoleCreate) -> Role:
        role = await self._role_repository.create(role_data)

        if role_data.scope_aliases:
            permission_ids = await self._parse_scope_aliases(role_data.scope_aliases)
            await self._role_repository.set_role_permissions(role.id, permission_ids)

        return await self._role_repository.get_with_permissions(role.id)

    async def update_role(self, role_id: int, role_data: RoleUpdate) -> Role:
        role = await self._role_repository.update(role_id, role_data)
        if not role:
            raise exceptions.NotFoundError(f"Role with id {role_id} not found")

        if role_data.scope_aliases is not None:
            if role_data.scope_aliases:
                permission_ids = await self._parse_scope_aliases(role_data.scope_aliases)
                await self._role_repository.set_role_permissions(role.id, permission_ids)
            else:
                await self._role_repository.set_role_permissions(role.id, [])

        return await self._role_repository.get_with_permissions(role.id)

    async def delete_role(self, role_id: int) -> None:
        deleted = await self._role_repository.delete(role_id)
        if not deleted:
            raise exceptions.NotFoundError(f"Role with id {role_id} not found")

    async def assign_roles_to_user(self, user_id: int, role_ids: List[int]) -> None:
        await self._role_repository.assign_roles_to_user(user_id, role_ids)

    async def get_or_create_role(self, name: str, description: Optional[str] = None) -> Role:
        role = await self._role_repository.get_or_create(name, description)
        return await self._role_repository.get_with_permissions(role.id)

    async def set_role_permissions(self, role_id: int, permission_ids: List[int]) -> None:
        await self._role_repository.set_role_permissions(role_id, permission_ids)

    async def get_user_role_names(self, user_id: int) -> List[str]:
        roles = await self._role_repository.get_user_roles(user_id)
        return [role.name for role in roles]

    async def get_user_role_ids(self, user_id: int) -> List[int]:
        roles = await self._role_repository.get_user_roles(user_id)
        return [role.id for role in roles]

    async def user_has_role(self, user_id: int, role_name: str) -> bool:
        roles = await self._role_repository.get_user_roles(user_id)
        return any(role.name == role_name for role in roles)

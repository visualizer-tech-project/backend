import uuid
from typing import List, Optional

from app.models.role import RolePublic, RoleCreate, RoleUpdate
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

    async def get_roles(self) -> List[RolePublic]:
        roles = await self._role_repository.get_all()
        result = []
        for role in roles:
            await self._role_repository.session.refresh(role, ['permissions'])
            result.append(RolePublic.model_validate(role))
        return result

    async def get_role_by_id(self, role_id: uuid.UUID) -> Optional[RolePublic]:
        role = await self._role_repository.get_with_permissions(role_id)
        if role:
            return RolePublic.model_validate(role)
        return None

    async def get_role_by_name(self, name: str) -> Optional[RolePublic]:
        role = await self._role_repository.get_by_name(name)
        if role:
            await self._role_repository.session.refresh(role, ['permissions'])
            return RolePublic.model_validate(role)
        return None

    async def create_role(self, role_data: RoleCreate) -> RolePublic:
        role = await self._role_repository.create(role_data)

        if role_data.scope_aliases:
            permission_ids = []
            for alias in role_data.scope_aliases:
                parts = alias.split(':', 1)
                if len(parts) == 2:
                    subject, action = parts
                    perm = await self._permission_repository.get_or_create(subject, action)
                    permission_ids.append(perm.id)
            await self._role_repository.set_permissions(role.id, permission_ids)

        await self._role_repository.session.refresh(role, ['permissions'])
        return RolePublic.model_validate(role)

    async def update_role(self, role_id: uuid.UUID, role_data: RoleUpdate) -> Optional[RolePublic]:
        role = await self._role_repository.update(role_id, role_data)
        if not role:
            return None

        if role_data.scope_aliases:
            permission_ids = []
            for alias in role_data.scope_aliases:
                parts = alias.split(':', 1)
                if len(parts) == 2:
                    subject, action = parts
                    perm = await self._permission_repository.get_or_create(subject, action)
                    permission_ids.append(perm.id)
            await self._role_repository.set_permissions(role.id, permission_ids)

        await self._role_repository.session.refresh(role, ['permissions'])
        return RolePublic.model_validate(role)

    async def delete_role(self, role_id: uuid.UUID) -> bool:
        return await self._role_repository.delete(role_id)

    async def assign_roles_to_user(self, user_id: int, role_ids: List[uuid.UUID]) -> None:
        await self._role_repository.assign_roles_to_user(user_id, role_ids)

    async def get_or_create_role(self, name: str, description: Optional[str] = None) -> RolePublic:
        role = await self._role_repository.get_or_create(name, description)
        await self._role_repository.session.refresh(role, ['permissions'])
        return RolePublic.model_validate(role)
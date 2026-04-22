import uuid
from typing import List, Optional

from app.core import exceptions
from app.models.permission import PermissionPublic, PermissionCreate
from app.repositories.permission import PermissionRepository


class PermissionService:
    def __init__(self, permission_repository: PermissionRepository):
        self._permission_repository = permission_repository

    async def get_permissions(self) -> List[PermissionPublic]:
        permissions = await self._permission_repository.get_all()
        return [PermissionPublic.model_validate(p) for p in permissions]

    async def get_permission_by_id(self, permission_id: uuid.UUID) -> PermissionPublic:
        permission = await self._permission_repository.get_by_id(permission_id)
        if not permission:
            raise exceptions.NotFoundError(f"Permission with id {permission_id} not found")
        return PermissionPublic.model_validate(permission)

    async def get_or_create_permission(self, subject: str, action: str) -> PermissionPublic:
        permission = await self._permission_repository.get_or_create(subject, action)
        return PermissionPublic.model_validate(permission)

    async def create_permission(self, permission_data: PermissionCreate) -> PermissionPublic:
        permission = await self._permission_repository.create(permission_data)
        return PermissionPublic.model_validate(permission)

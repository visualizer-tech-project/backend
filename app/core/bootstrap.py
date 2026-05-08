from typing import Set

from sqlalchemy import text
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.rbac import INITIAL_SUBJECTS, INITIAL_ACTIONS, INITIAL_PERMISSION_SCHEMA
from app.core.settings import settings
from app.core.hasher import hash_password
from app.models.user import User, UserCreate, UserRole
from app.services.permission import PermissionService
from app.services.role import RoleService
from app.services.user import UserService

BOOTSTRAP_LOCK_ID = 123456789


class Bootstrapper:
    def __init__(
        self,
        user_service: UserService,
        role_service: RoleService,
        permission_service: PermissionService,
        session: AsyncSession,
    ):
        self._user_service = user_service
        self._role_service = role_service
        self._permission_service = permission_service
        self._session = session

    async def bootstrap_app(self) -> None:
        await self._session.exec(
            text('SELECT pg_advisory_lock(:lock_id)').bindparams(lock_id=BOOTSTRAP_LOCK_ID)
        )
        try:
            await self._do_bootstrap()
        finally:
            await self._session.exec(
                text('SELECT pg_advisory_unlock(:lock_id)').bindparams(lock_id=BOOTSTRAP_LOCK_ID)
            )

    async def _do_bootstrap(self) -> None:
        all_permission_ids: Set[int] = set()
        for subject in INITIAL_SUBJECTS:
            for action in INITIAL_ACTIONS:
                perm = await self._permission_service.get_or_create_permission(
                    subject, action
                )
                all_permission_ids.add(perm.id)

        admin_role = await self._role_service.get_or_create_role(
            name=settings.rbac.admin_role,
            description='Administrator with full access',
        )
        await self._role_service.set_role_permissions(
            admin_role.id,
            list(all_permission_ids),
        )

        for role_name, scope_aliases in INITIAL_PERMISSION_SCHEMA.items():
            if role_name == settings.rbac.admin_role:
                continue

            role = await self._role_service.get_or_create_role(
                name=role_name,
                description=f'Role: {role_name}',
            )

            if not scope_aliases:
                continue

            permission_ids = []
            for alias in scope_aliases:
                parts = alias.split(':', 1)
                if len(parts) == 2:
                    subject, action = parts
                    perm = await self._permission_service.get_or_create_permission(
                        subject, action
                    )
                    permission_ids.append(perm.id)

            await self._role_service.set_role_permissions(role.id, permission_ids)

        existing_admin = await self._user_service.get_user_by_email(
            settings.rbac.admin_email
        )
        if not existing_admin:
            admin_user = UserCreate(
                email=settings.rbac.admin_email,
                first_name=settings.rbac.admin_first_name,
                last_name=settings.rbac.admin_last_name,
                role=UserRole.ADMIN,
                hashed_password=hash_password(settings.rbac.admin_password),
            )
            user = await self._user_service.create_user(admin_user)

            admin_role_obj = await self._role_service.get_role_by_name(
                settings.rbac.admin_role
            )
            if admin_role_obj:
                await self._role_service.assign_roles_to_user(
                    user.id, [admin_role_obj.id]
                )
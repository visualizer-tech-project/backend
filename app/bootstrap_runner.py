import asyncio

from app.dependencies.session import get_session
from app.repositories.user import UserRepository
from app.repositories.permission import PermissionRepository
from app.repositories.role import RoleRepository
from app.services.user import UserService
from app.services.permission import PermissionService
from app.services.role import RoleService
from app.core.bootstrap import Bootstrapper


async def main():
    async for session in get_session():
        permission_repository = PermissionRepository(session)
        permission_service = PermissionService(permission_repository)

        role_repository = RoleRepository(session)
        role_service = RoleService(role_repository, permission_repository)

        user_repository = UserRepository(session)
        user_service = UserService(user_repository)

        bootstrapper = Bootstrapper(
            user_service=user_service,
            role_service=role_service,
            permission_service=permission_service,
        )
        await bootstrapper.bootstrap_app()
        print('Bootstrap completed successfully')
        break


if __name__ == '__main__':
    asyncio.run(main())

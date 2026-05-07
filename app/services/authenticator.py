from typing import Optional

from fastapi import Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.auth import JWTHandler
from app.dependencies.session import get_session
from app.models.user import User
from app.repositories.role import RoleRepository
from app.repositories.user import UserRepository


class AuthenticatorService:
    def __init__(self, session: AsyncSession = Depends(get_session)):
        self._session = session
        self._user_repo = UserRepository(session)
        self._role_repo = RoleRepository(session)

    async def get_user_from_token(self, access_token: str) -> Optional[User]:
        payload = JWTHandler.decode_token(access_token)
        if not payload:
            return None

        user_id = payload.get('sub')
        if not user_id:
            return None

        return await self._user_repo.get_by_id(int(user_id))

    async def check_permissions(self, user: User, required_scopes: list[str]) -> bool:
        if not required_scopes:
            return True

        user_roles = await self._role_repo.get_user_roles(user.id)

        user_scopes = set()
        for role in user_roles:
            await self._session.refresh(role, ['permissions'])
            for permission in role.permissions:
                user_scopes.add(f'{permission.subject}:{permission.action}')

        for scope in required_scopes:
            if scope not in user_scopes:
                return False

        return True

    async def authenticate(
        self,
        access_token: str,
        required_scopes: list[str],
    ) -> Optional[User]:
        user = await self.get_user_from_token(access_token)
        if not user:
            return None

        if not await self.check_permissions(user, required_scopes):
            return None

        return user

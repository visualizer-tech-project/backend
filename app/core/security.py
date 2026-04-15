from passlib.context import CryptContext

from typing import Annotated, Optional

from fastapi import Depends, Security
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.auth import JWTHandler
from app.core.rbac import PERMISSION_DESCRIPTIONS
from app.dependencies.session import get_session
from app.models.user import User
from app.repositories.role import RoleRepository
from app.repositories.user import UserRepository


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl='/api/v1/auth/login',
    refreshUrl='/api/v1/auth/refresh',
    scopes=PERMISSION_DESCRIPTIONS,
)

AccessTokenDep = Annotated[str, Depends(oauth2_scheme)]


class Authenticator:
    def __init__(self):
        pass

    async def _get_user_token_data(self, access_token: str) -> Optional[tuple[int, str]]:
        payload = JWTHandler.decode_token(access_token)
        if not payload:
            return None
        user_id = payload.get('sub')
        access_token_jti = payload.get('jti')
        if not user_id or not access_token_jti:
            return None
        return int(user_id), access_token_jti

    async def authenticate_user(
        self,
        access_token: AccessTokenDep,
        security_scopes: SecurityScopes,
        session: AsyncSession,
    ) -> Optional[User]:
        token_data = await self._get_user_token_data(access_token)
        if token_data is None:
            return None

        user_id, _ = token_data

        user_repository = UserRepository(session)
        user = await user_repository.get_by_id(user_id)
        if user is None:
            return None

        if not security_scopes.scopes:
            return user

        role_repository = RoleRepository(session)
        user_roles = await role_repository.get_user_roles(user_id)

        user_scopes = set()
        for role in user_roles:
            await session.refresh(role, ['permissions'])
            for permission in role.permissions:
                user_scopes.add(f'{permission.subject}:{permission.action}')

        for security_scope in security_scopes.scopes:
            if security_scope not in user_scopes:
                return None

        return user


authenticator = Authenticator()


async def get_current_user(
    access_token: AccessTokenDep,
    security_scopes: SecurityScopes,
    session: AsyncSession = Depends(get_session),
) -> Optional[User]:
    return await authenticator.authenticate_user(access_token, security_scopes, session)


CurrentUser = Annotated[Optional[User], Security(get_current_user)]

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
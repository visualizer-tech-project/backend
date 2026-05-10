from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core import exceptions
from app.core.rbac import PERMISSION_DESCRIPTIONS
from app.dependencies.services import get_user_repo, get_role_repo
from app.models.user import User
from app.repositories.role import RoleRepository
from app.repositories.user import UserRepository
from app.services.authenticator import AuthenticatorService

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl='/api/v1/auth/login',
    refreshUrl='/api/v1/auth/refresh',
    scopes=PERMISSION_DESCRIPTIONS,
)

AccessTokenDep = Annotated[str, Depends(oauth2_scheme)]


def get_authenticator(session: AsyncSession = Depends(get_session)) -> AuthenticatorService:
    return AuthenticatorService(session)


async def get_current_user(
    access_token: AccessTokenDep,
    security_scopes: SecurityScopes,
    user_repo: UserRepository = Depends(get_user_repo),
    role_repo: RoleRepository = Depends(get_role_repo),
) -> User:
    authenticator = AuthenticatorService(user_repo, role_repo)
    user = await authenticator.authenticate(
        access_token,
        security_scopes.scopes,
    )
    if user is None:
        raise exceptions.UnauthorizedError("Invalid or expired token")
    return user

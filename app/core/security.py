from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core import exceptions
from app.core.rbac import PERMISSION_DESCRIPTIONS
from app.dependencies.session import get_session
from app.models.user import User
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
    authenticator: AuthenticatorService = Depends(get_authenticator),
) -> User:
    user = await authenticator.authenticate(
        access_token,
        security_scopes.scopes,
    )
    if user is None:
        raise exceptions.UnauthorizedError('Invalid or expired token')
    return user
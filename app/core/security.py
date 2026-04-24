from typing import Annotated

from fastapi import Depends, Security
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


async def get_current_user(
    access_token: AccessTokenDep,
    security_scopes: SecurityScopes,
    session: AsyncSession = Depends(get_session),
) -> User:
    authenticator = AuthenticatorService(session)
    user = await authenticator.authenticate(
        access_token,
        security_scopes.scopes,
    )
    if user is None:
        raise exceptions.UnauthorizedError("Invalid or expired token")
    return user


CurrentUser = Annotated[User, Security(get_current_user)]

from fastapi import APIRouter, Depends, Response, Request, status, Cookie

from app.core import responses
from app.core.security import oauth2_scheme
from app.dependencies.services import get_auth_service
from app.models.user import User
from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    TokenResponse,
    RefreshResponse,
    LogoutResponse,
    MeResponse,
)
from app.services.auth import AuthService
from app.core.constants import REFRESH_TOKEN_COOKIE_NAME, REFRESH_TOKEN_COOKIE_MAX_AGE

router = APIRouter(prefix='/auth', tags=['auth'])


def set_refresh_token_cookie(response: Response, refresh_token: str) -> None:
    response.set_cookie(
        key=REFRESH_TOKEN_COOKIE_NAME,
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite='lax',
        max_age=REFRESH_TOKEN_COOKIE_MAX_AGE,
    )


def clear_refresh_token_cookie(response: Response) -> None:
    response.delete_cookie(
        key=REFRESH_TOKEN_COOKIE_NAME,
        httponly=True,
        secure=True,
        samesite='lax',
    )


@router.post(
    '/register',
    response_model=User,
    status_code=status.HTTP_201_CREATED,
    responses={
        **responses.bad_request_responses,
        **responses.conflict_responses,
        **responses.common_responses,
    }
)
async def register(
    register_data: RegisterRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> User:
    try:
        user = await auth_service.register(register_data)
        return user
    except ValueError as e:
        if 'already exists' in str(e):
            responses.raise_conflict(str(e))
        responses.raise_bad_request(str(e))


@router.post(
    '/login',
    response_model=TokenResponse,
    responses={
        **responses.auth_responses,
        **responses.common_responses,
    }
)
async def login(
    response: Response,
    login_data: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    try:
        token_response = await auth_service.login(login_data)
        set_refresh_token_cookie(response, token_response.refresh_token)
        return token_response
    except ValueError as e:
        responses.raise_unauthorized(str(e))


@router.post(
    '/refresh',
    response_model=RefreshResponse,
    responses={
        **responses.auth_responses,
        **responses.common_responses,
    }
)
async def refresh_token(
    response: Response,
    refresh_token: str = Cookie(None, alias=REFRESH_TOKEN_COOKIE_NAME),
    auth_service: AuthService = Depends(get_auth_service),
) -> RefreshResponse:
    if not refresh_token:
        responses.raise_unauthorized('Refresh token not found')

    try:
        refresh_response = await auth_service.refresh(refresh_token)
        set_refresh_token_cookie(response, refresh_response.refresh_token)
        return refresh_response
    except ValueError as e:
        responses.raise_unauthorized(str(e))


@router.post(
    '/logout',
    response_model=LogoutResponse,
    responses={**responses.common_responses}
)
async def logout(
    refresh_token: str = Cookie(None, alias=REFRESH_TOKEN_COOKIE_NAME),
    auth_service: AuthService = Depends(get_auth_service),
) -> LogoutResponse:
    if not refresh_token:
        return LogoutResponse(success=True)

    try:
        success = await auth_service.logout(refresh_token)
        if success:
            response = Response()
            clear_refresh_token_cookie(response)
            return LogoutResponse(success=True)
        return LogoutResponse(success=False)
    except Exception:
        responses.raise_server_error()


@router.get(
    '/me',
    response_model=MeResponse,
    responses={
        **responses.auth_responses,
        **responses.common_responses,
    }
)
async def get_me(
    token: str = Depends(oauth2_scheme),
    auth_service: AuthService = Depends(get_auth_service),
) -> MeResponse:
    user = await auth_service.get_user_from_access_token(token)
    if not user:
        responses.raise_unauthorized('Invalid or expired token')

    return MeResponse.model_validate(user)

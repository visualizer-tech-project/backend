import json

from fastapi import APIRouter, Depends, Response, Request, status

from app.core import responses
from app.dependencies.services import get_auth_service
from app.models.user import UserPublic
from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    TokenResponse,
    RefreshResponse,
    LogoutResponse,
    MeResponse,
)
from app.services.auth import AuthService
from app.core.auth import jwt_bearer
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


def get_refresh_token_from_cookie(request: Request) -> str | None:
    return request.cookies.get(REFRESH_TOKEN_COOKIE_NAME)


@router.post(
    '/register',
    response_model=UserPublic,
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
) -> UserPublic:
    try:
        user = await auth_service.register(register_data)
        return UserPublic.model_validate(user)
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
    request: Request,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    body = await request.body()
    login_data = LoginRequest(**json.loads(body))

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
    request: Request,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service),
) -> RefreshResponse:
    refresh_token = get_refresh_token_from_cookie(request)

    if not refresh_token:
        responses.raise_unauthorized('Refresh token not found')

    try:
        refresh_response = await auth_service.refresh(refresh_token)
        set_refresh_token_cookie(response, refresh_response.refresh_token)
        return refresh_response
    except ValueError as e:
        clear_refresh_token_cookie(response)
        responses.raise_unauthorized(str(e))


@router.post(
    '/logout',
    response_model=LogoutResponse,
    responses={**responses.common_responses}
)
async def logout(
    request: Request,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service),
) -> LogoutResponse:
    refresh_token = get_refresh_token_from_cookie(request)

    clear_refresh_token_cookie(response)

    if not refresh_token:
        return LogoutResponse(success=True)

    try:
        success = await auth_service.logout(refresh_token)
        return LogoutResponse(success=success)
    except Exception:
        return LogoutResponse(success=True)


@router.get(
    '/me',
    response_model=MeResponse,
    responses={
        **responses.auth_responses,
        **responses.common_responses,
    }
)
async def get_me(
    token: str = Depends(jwt_bearer),
    auth_service: AuthService = Depends(get_auth_service),
) -> MeResponse:
    user = await auth_service.get_user_from_access_token(token)

    if not user:
        responses.raise_unauthorized('Invalid or expired token')

    return MeResponse(
        id=user.id,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        role=user.role.value,
    )
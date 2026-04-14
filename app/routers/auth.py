import json

from fastapi import APIRouter, Depends, HTTPException, status, Response, Request

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


@router.post('/register', response_model=UserPublic, status_code=status.HTTP_201_CREATED)
async def register(
    register_data: RegisterRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> UserPublic:
    try:
        user = await auth_service.register(register_data)
        return UserPublic.model_validate(user)
    except ValueError as e:
        if 'already exists' in str(e):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post('/login', response_model=TokenResponse)
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
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.post('/refresh', response_model=RefreshResponse)
async def refresh_token(
    request: Request,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service),
) -> RefreshResponse:
    refresh_token = get_refresh_token_from_cookie(request)

    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Refresh token not found',
        )

    try:
        refresh_response = await auth_service.refresh(refresh_token)
        set_refresh_token_cookie(response, refresh_response.refresh_token)
        return refresh_response
    except ValueError as e:
        clear_refresh_token_cookie(response)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.post('/logout', response_model=LogoutResponse)
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


@router.get('/me', response_model=MeResponse)
async def get_me(
    token: str = Depends(jwt_bearer),
    auth_service: AuthService = Depends(get_auth_service),
) -> MeResponse:
    user = await auth_service.get_user_from_access_token(token)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid or expired token',
        )

    return MeResponse(
        id=user.id,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        role=user.role.value,
    )

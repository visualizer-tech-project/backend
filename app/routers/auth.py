from fastapi import APIRouter, Depends, Response, status, Cookie, BackgroundTasks, Request, Security
from fastapi.security import OAuth2PasswordRequestForm

from app.core import exceptions, responses
from app.core.rate_limiter import limiter
from app.core.security import get_current_user
from app.dependencies import get_auth_service
from app.dependencies.auth import CurrentUser
from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    TokenResponse,
    RefreshResponse,
    LogoutResponse,
    MeResponse,
    VerifyAccountRequest,
    ChangePasswordRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    MessageResponse,
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
    response_model=MeResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        **responses.bad_request_responses,
        **responses.conflict_responses,
        **responses.common_responses,
    }
)
@limiter.limit("5/minute")
async def register(
    request: Request,
    response: Response,
    register_data: RegisterRequest,
    background_tasks: BackgroundTasks,
    auth_service: AuthService = Depends(get_auth_service),
) -> MeResponse:
    try:
        user = await auth_service.register(register_data, background_tasks)
        return MeResponse.model_validate(user)
    except ValueError as e:
        if 'already exists' in str(e):
            raise exceptions.ConflictError(str(e))
        raise exceptions.BadRequestError(str(e))


@router.post(
    '/verify',
    response_model=MessageResponse,
    responses={
        **responses.bad_request_responses,
        **responses.detail_responses,
        **responses.common_responses,
    }
)
@limiter.limit("10/minute")
async def verify_account(
    request: Request,
    response: Response,
    verify_data: VerifyAccountRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> MessageResponse:
    await auth_service.verify_account(verify_data)
    return MessageResponse(
        message="Account verified successfully. You can now login.",
        success=True
    )


@router.post(
    '/login',
    response_model=TokenResponse,
    responses={
        **responses.auth_responses,
        **responses.common_responses,
    }
)
@limiter.limit("5/minute")
async def login(
    request: Request,
    response: Response,
    login_data: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    try:
        token_response = await auth_service.login(login_data)
        set_refresh_token_cookie(response, token_response.refresh_token)
        return token_response
    except ValueError as e:
        raise exceptions.UnauthorizedError(str(e))


@router.post(
    '/refresh',
    response_model=RefreshResponse,
    responses={
        **responses.auth_responses,
        **responses.common_responses,
    }
)
@limiter.limit("10/minute")
async def refresh_token(
    request: Request,
    response: Response,
    refresh_token: str = Cookie(None, alias=REFRESH_TOKEN_COOKIE_NAME),
    auth_service: AuthService = Depends(get_auth_service),
) -> RefreshResponse:
    if not refresh_token:
        raise exceptions.UnauthorizedError('Refresh token not found')

    try:
        refresh_response = await auth_service.refresh(refresh_token)
        set_refresh_token_cookie(response, refresh_response.refresh_token)
        return refresh_response
    except ValueError as e:
        raise exceptions.UnauthorizedError(str(e))


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
        raise exceptions.InternalServerError()


@router.get(
    '/me',
    response_model=MeResponse,
    responses={
        **responses.auth_responses,
        **responses.common_responses,
    }
)
@limiter.limit("30/minute")
async def get_me(
    request: Request,
    response: Response,
    current_user: CurrentUser = Security(get_current_user, scopes=['profile:read']),
) -> MeResponse:
    return MeResponse.model_validate(current_user)


@router.post(
    '/forgot-password',
    response_model=MessageResponse,
    responses={
        **responses.bad_request_responses,
        **responses.common_responses,
    }
)
@limiter.limit("3/minute")
async def forgot_password(
    request: Request,
    response: Response,
    forgot_data: ForgotPasswordRequest,
    background_tasks: BackgroundTasks,
    auth_service: AuthService = Depends(get_auth_service),
) -> MessageResponse:
    await auth_service.forgot_password(forgot_data, background_tasks)
    return MessageResponse(
        message="If the email exists in our system, a password reset link has been sent.",
        success=True
    )


@router.post(
    '/reset-password',
    response_model=MessageResponse,
    responses={
        **responses.bad_request_responses,
        **responses.detail_responses,
        **responses.common_responses,
    }
)
@limiter.limit("5/minute")
async def reset_password(
    request: Request,
    response: Response,
    reset_data: ResetPasswordRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> MessageResponse:
    await auth_service.reset_password(reset_data)
    return MessageResponse(
        message="Password has been reset successfully. You can now login with the new password.",
        success=True
    )


@router.post(
    '/change-password',
    response_model=MessageResponse,
    responses={
        **responses.auth_responses,
        **responses.bad_request_responses,
        **responses.common_responses,
    }
)
@limiter.limit("5/minute")
async def change_password(
    request: Request,
    response: Response,
    change_data: ChangePasswordRequest,
    current_user: CurrentUser = Security(get_current_user, scopes=['profile:read']),
    auth_service: AuthService = Depends(get_auth_service),
) -> MessageResponse:
    await auth_service.change_password(current_user.id, change_data)
    return MessageResponse(
        message="Password has been changed successfully. Please login again with the new password.",
        success=True
    )

@router.post('/oauth/token', response_model=TokenResponse, include_in_schema=False)
async def oauth_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    login_data = LoginRequest(
        email=form_data.username,
        password=form_data.password
    )
    token_response = await auth_service.login(login_data)
    return token_response

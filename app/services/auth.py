import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import BackgroundTasks

from app.core import exceptions, settings
from app.core.auth import JWTHandler
from app.core.hasher import hash_password, verify_password
from app.models.user import User, UserCreate, UserRole, AccountStatus
from app.models.email import EmailAction
from app.repositories.user import UserRepository
from app.repositories.refresh_session import RefreshSessionRepository
from app.repositories.role import RoleRepository
from app.repositories.email import EmailRepository
from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    TokenResponse,
    RefreshResponse,
    VerifyAccountRequest,
    ChangePasswordRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
)
from app.services.email import EmailService


class AuthService:
    def __init__(
            self,
            user_repo: UserRepository,
            refresh_session_repo: RefreshSessionRepository,
            role_repo: RoleRepository,
            email_repo: EmailRepository,
    ) -> None:
        self._user_repo = user_repo
        self._refresh_session_repo = refresh_session_repo
        self._role_repo = role_repo
        self._email_repo = email_repo

    async def _create_tokens_and_session(self, user_id: int) -> tuple[str, str]:
        access_jti = str(uuid.uuid4())
        refresh_jti = str(uuid.uuid4())

        access_token = JWTHandler.create_access_token(user_id, access_jti)
        refresh_token = JWTHandler.create_refresh_token(user_id, refresh_jti)

        payload = JWTHandler.decode_token(refresh_token)
        if not payload:
            raise exceptions.InternalServerError("Failed to decode refresh token")
        expires_at = datetime.fromtimestamp(payload['exp'], tz=timezone.utc)

        await self._refresh_session_repo.create_session(
            user_id=user_id,
            refresh_token_jti=refresh_jti,
            expires_at=expires_at,
        )

        return access_token, refresh_token

    async def register(
            self,
            register_data: RegisterRequest,
            background_tasks: BackgroundTasks,
    ) -> User:
        email_str = str(register_data.email)

        existing_user = await self._user_repo.get_by_email(email_str)
        if existing_user:
            raise exceptions.ConflictError(
                f"User with email {email_str} already exists"
            )

        user_create = UserCreate(
            email=email_str,
            first_name=register_data.first_name,
            last_name=register_data.last_name,
            role=UserRole.STUDENT,
            status=AccountStatus.CREATED,
            hashed_password=hash_password(register_data.password),
        )

        user = await self._user_repo.create(user_create)
        public_role = await self._role_repo.get_by_name(settings.rbac.public_role)
        if public_role:
            await self._role_repo.assign_roles_to_user(user.id, [public_role.id])
        notification = await self._email_repo.create_notification(
            user_id=user.id,
            action=EmailAction.VERIFY_ACCOUNT,
        )
        email_service = EmailService(background_tasks)
        verification_link = (
            f"{settings.email.base_url}/api/v1/auth/verify?code={notification.code}"
        )
        await email_service.send_verification_email(
            email_to=str(user.email),
            verification_code=str(notification.code),
            verification_link=verification_link,
        )
        return user

    async def verify_account(self, verify_data: VerifyAccountRequest) -> None:
        notification = await self._email_repo.get_by_code(verify_data.code)
        if not notification:
            raise exceptions.NotFoundError("Verification code not found")
        if not notification.is_valid:
            raise exceptions.BadRequestError(
                "Verification code is invalid, expired or already used"
            )
        user = await self._user_repo.get_by_id(notification.user_id)
        if not user:
            raise exceptions.NotFoundError("User not found")
        user.status = AccountStatus.CONFIRMED
        await self._user_repo.save(user)
        await self._email_repo.mark_as_used(notification)

    async def login(self, login_data: LoginRequest) -> TokenResponse:
        email_str = str(login_data.email)
        user = await self._user_repo.get_by_email(email_str)
        if not user:
            raise exceptions.UnauthorizedError("Invalid email or password")
        if user.status != AccountStatus.CONFIRMED:
            raise exceptions.UnauthorizedError(
                "Account is not confirmed. Please verify your email first."
            )

        if not verify_password(login_data.password, user.hashed_password):
            raise exceptions.UnauthorizedError("Invalid email or password")

        access_token, refresh_token = await self._create_tokens_and_session(user.id)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
        )

    async def refresh(self, refresh_token: str) -> RefreshResponse:
        payload = JWTHandler.decode_token(refresh_token)
        if not payload:
            raise exceptions.UnauthorizedError("Invalid refresh token")

        refresh_token_jti = payload.get('jti')
        if not refresh_token_jti:
            raise exceptions.UnauthorizedError("Invalid refresh token: missing jti")

        session = await self._refresh_session_repo.get_by_jti(refresh_token_jti)
        if not session:
            raise exceptions.UnauthorizedError("Refresh session not found")

        if not session.is_valid:
            raise exceptions.UnauthorizedError("Refresh session is invalid")

        if session.is_expired():
            raise exceptions.UnauthorizedError("Refresh session has expired")

        user_id = int(payload['sub'])
        user = await self._user_repo.get_by_id(user_id)
        if not user:
            raise exceptions.UnauthorizedError("User not found")

        await self._refresh_session_repo.invalidate_session(refresh_token_jti)

        access_token, new_refresh_token = await self._create_tokens_and_session(user.id)

        return RefreshResponse(
            access_token=access_token,
            refresh_token=new_refresh_token,
        )

    async def logout(self, refresh_token: str) -> bool:
        payload = JWTHandler.decode_token(refresh_token)
        if not payload:
            return False

        refresh_token_jti = payload.get('jti')
        if not refresh_token_jti:
            return False

        return await self._refresh_session_repo.invalidate_session(refresh_token_jti)

    async def get_user_from_access_token(self, access_token: str) -> Optional[User]:
        payload = JWTHandler.decode_token(access_token)
        if not payload:
            return None

        user_id = int(payload['sub'])
        return await self._user_repo.get_by_id(user_id)

    async def forgot_password(
            self,
            request: ForgotPasswordRequest,
            background_tasks: BackgroundTasks,
    ) -> None:
        email_str = str(request.email)
        user = await self._user_repo.get_by_email(email_str)
        if not user:
            return

        notification = await self._email_repo.create_notification(
            user_id=user.id,
            action=EmailAction.CHANGE_PASSWORD,
        )

        email_service = EmailService(background_tasks)
        reset_link = (
            f"{settings.email.base_url}/api/v1/auth/reset-password?code={notification.code}"
        )
        await email_service.send_change_password_email(
            email_to=str(user.email),
            reset_code=str(notification.code),
            reset_link=reset_link,
        )

    async def reset_password(self, request: ResetPasswordRequest) -> None:
        if request.new_password != request.confirm_password:
            raise exceptions.BadRequestError("Passwords do not match")
        notification = await self._email_repo.get_by_code(request.code)
        if not notification:
            raise exceptions.NotFoundError("Reset code not found")
        if not notification.is_valid:
            raise exceptions.BadRequestError(
                "Reset code is invalid, expired or already used"
            )
        user = await self._user_repo.get_by_id(notification.user_id)
        if not user:
            raise exceptions.NotFoundError("User not found")
        user.hashed_password = hash_password(request.new_password)
        await self._user_repo.save(user)
        await self._refresh_session_repo.invalidate_all_user_sessions(user.id)
        await self._email_repo.mark_as_used(notification)

    async def change_password(
            self,
            user_id: int,
            request: ChangePasswordRequest,
    ) -> None:
        if request.new_password != request.confirm_password:
            raise exceptions.BadRequestError("Passwords do not match")
        user = await self._user_repo.get_by_id(user_id)
        if not user:
            raise exceptions.NotFoundError("User not found")
        if request.old_password:
            if not verify_password(request.old_password, user.hashed_password):
                raise exceptions.BadRequestError("Old password is incorrect")
        user.hashed_password = hash_password(request.new_password)
        await self._user_repo.save(user)
        await self._refresh_session_repo.invalidate_all_user_sessions(user.id)

from app.dependencies.services import (
    get_user_repo,
    get_refresh_session_repo,
    get_role_repo,
    get_email_repo,
)

async def get_auth_service(
    user_repo: UserRepository = Depends(get_user_repo),
    refresh_session_repo: RefreshSessionRepository = Depends(get_refresh_session_repo),
    role_repo: RoleRepository = Depends(get_role_repo),
    email_repo: EmailRepository = Depends(get_email_repo),
) -> AuthService:
    return AuthService(
        user_repo=user_repo,
        refresh_session_repo=refresh_session_repo,
        role_repo=role_repo,
        email_repo=email_repo,
    )
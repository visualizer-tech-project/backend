import uuid
from datetime import datetime, timezone
from typing import Optional

from app.core import settings
from app.core.auth import JWTHandler
from app.core.hasher import hash_password, verify_password
from app.models.user import User, UserCreate, UserRole
from app.repositories.user import UserRepository
from app.repositories.refresh_session import RefreshSessionRepository
from app.repositories.role import RoleRepository
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse, RefreshResponse


class AuthService:
    def __init__(
        self,
        user_repo: UserRepository,
        refresh_session_repo: RefreshSessionRepository,
        role_repo: RoleRepository,
    ) -> None:
        self._user_repo = user_repo
        self._refresh_session_repo = refresh_session_repo
        self._role_repo = role_repo

    async def _create_tokens_and_session(self, user_id: int) -> tuple[str, str]:
        access_jti = str(uuid.uuid4())
        refresh_jti = str(uuid.uuid4())

        access_token = JWTHandler.create_access_token(user_id, access_jti)
        refresh_token = JWTHandler.create_refresh_token(user_id, refresh_jti)

        payload = JWTHandler.decode_token(refresh_token)
        expires_at = datetime.fromtimestamp(payload['exp'], tz=timezone.utc)

        await self._refresh_session_repo.create_session(
            user_id=user_id,
            refresh_token_jti=refresh_jti,
            expires_at=expires_at,
        )

        return access_token, refresh_token

    async def register(self, register_data: RegisterRequest) -> User:
        existing_user = await self._user_repo.get_by_email(register_data.email)
        if existing_user:
            raise ValueError('User with this email already exists')

        user_create = UserCreate(
            email=register_data.email,
            first_name=register_data.first_name,
            last_name=register_data.last_name,
            role=UserRole.STUDENT,
            hashed_password=hash_password(register_data.password),
        )

        user = await self._user_repo.create(user_create)

        public_role = await self._role_repo.get_by_name(settings.rbac.public_role)
        if public_role:
            await self._role_repo.assign_roles_to_user(user.id, [public_role.id])

        return user

    async def login(self, login_data: LoginRequest) -> TokenResponse:
        user = await self._user_repo.get_by_email(login_data.email)
        if not user:
            raise ValueError('Invalid credentials')

        if not verify_password(login_data.password, user.hashed_password):
            raise ValueError('Invalid credentials')

        access_token, refresh_token = await self._create_tokens_and_session(user.id)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
        )

    async def refresh(self, refresh_token: str) -> RefreshResponse:
        payload = JWTHandler.decode_token(refresh_token)
        if not payload:
            raise ValueError('Invalid refresh token')

        refresh_token_jti = payload.get('jti')
        if not refresh_token_jti:
            raise ValueError('Invalid refresh token: missing jti')

        session = await self._refresh_session_repo.get_by_jti(refresh_token_jti)
        if not session:
            raise ValueError('Refresh session not found')

        if not session.is_valid:
            raise ValueError('Refresh session is invalid')

        if session.is_expired():
            raise ValueError('Refresh session has expired')

        user_id = int(payload['sub'])
        user = await self._user_repo.get_by_id(user_id)
        if not user:
            raise ValueError('User not found')

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

from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.models.user import UserRole
from app.repositories.user import UserRepository
from app.schemas.token import Token
from app.schemas.user import LoginRequest, UserCreate, UserPublic

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


class AuthService:
    """Сервис аутентификации и авторизации"""

    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Проверить пароль"""
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """Получить хеш пароля"""
        return pwd_context.hash(password)

    def create_access_token(
        self,
        data: dict,
        expires_delta: Optional[timedelta] = None,
        secret_key: str = None,
        algorithm: str = 'HS256',
    ) -> str:
        """Создать JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=15)

        to_encode.update({'exp': expire})
        encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=algorithm)
        return encoded_jwt

    def decode_token(
        self, token: str, secret_key: str, algorithm: str = 'HS256'
    ) -> dict:
        """Декодировать JWT токен"""
        try:
            payload = jwt.decode(token, secret_key, algorithms=[algorithm])
            return payload
        except JWTError:
            return {}

    async def register(
        self,
        user_data: UserCreate,
        default_role: UserRole = UserRole.STUDENT,
    ) -> UserPublic:
        """Зарегистрировать нового пользователя"""
        if await self.user_repo.is_email_taken(user_data.email):
            raise ValueError('User with this email already exists')

        hashed_password = self.get_password_hash(user_data.password)

        user_dict = {
            'email': user_data.email,
            'hashed_password': hashed_password,
            'first_name': user_data.first_name,
            'last_name': user_data.last_name,
            'role': user_data.role or default_role,
        }

        user = await self.user_repo.create(user_dict)
        return UserPublic.model_validate(user)

    async def login(
        self,
        login_data: LoginRequest,
        secret_key: str,
        access_token_expire_minutes: int = 30,
    ) -> Token:
        """Аутентификация пользователя"""
        user = await self.user_repo.get_by_email(login_data.email)
        if not user:
            raise ValueError('Invalid credentials')

        if not self.verify_password(login_data.password, user.hashed_password):
            raise ValueError('Invalid credentials')

        scopes = self._get_user_scopes(user.role)

        access_token_expires = timedelta(minutes=access_token_expire_minutes)
        access_token = self.create_access_token(
            data={'sub': str(user.id), 'role': user.role.value, 'scopes': scopes},
            expires_delta=access_token_expires,
            secret_key=secret_key,
        )

        return Token(
            access_token=access_token,
            token_type='bearer',
            scope=' '.join(scopes),
        )

    def _get_user_scopes(self, role: UserRole) -> list[str]:
        """Получить список scopes на основе роли пользователя"""
        base_scopes = ['read:programs', 'read:courses', 'read:career-tracks']

        if role == UserRole.STUDENT:
            return base_scopes + ['read:users']

        if role == UserRole.TEACHER:
            return base_scopes + [
                'read:users',
                'write:courses',
                'delete:courses',
                'write:career-tracks',
                'delete:career-tracks',
            ]

        if role == UserRole.ADMIN:
            return [
                'read:users',
                'write:users',
                'read:programs',
                'write:programs',
                'delete:programs',
                'read:courses',
                'write:courses',
                'delete:courses',
                'read:career-tracks',
                'write:career-tracks',
                'delete:career-tracks',
                'admin:assign-teacher',
            ]

        return base_scopes

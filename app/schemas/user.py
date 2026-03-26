from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import EmailStr, Field

from app.schemas.base import BaseModelSchema, BaseSchema


class UserRole(str, Enum):
    """Роли пользователей"""

    ADMIN = 'admin'
    STUDENT = 'student'
    TEACHER = 'teacher'


class UserCreate(BaseSchema):
    """Схема для регистрации пользователя"""

    email: EmailStr = Field(..., max_length=255, description='Email пользователя')
    password: str = Field(..., min_length=6, max_length=128, description='Пароль')
    first_name: str = Field(..., min_length=1, max_length=100, description='Имя')
    last_name: str = Field(..., min_length=1, max_length=100, description='Фамилия')
    role: UserRole = Field(default=UserRole.STUDENT, description='Роль пользователя')


class UserUpdate(BaseSchema):
    """Схема для обновления пользователя"""

    first_name: Optional[str] = Field(
        None, min_length=1, max_length=100, description='Имя'
    )
    last_name: Optional[str] = Field(
        None, min_length=1, max_length=100, description='Фамилия'
    )
    role: Optional[UserRole] = Field(None, description='Роль пользователя')


class LoginRequest(BaseSchema):
    """Схема для входа в систему"""

    email: EmailStr = Field(..., description='Email пользователя')
    password: str = Field(..., description='Пароль')


class UserPublic(BaseModelSchema):
    """Публичная информация о пользователе"""

    email: EmailStr
    first_name: str
    last_name: str
    role: UserRole
    created_at: datetime


class UserDB(UserPublic):
    """Схема для работы с БД"""

    hashed_password: str

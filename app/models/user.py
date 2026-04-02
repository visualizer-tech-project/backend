from enum import Enum
from typing import Optional

from pydantic import EmailStr, Field
from sqlmodel import Field as SQLField
from sqlmodel import Relationship

from app.models.base import BaseModelSchema, BaseSchema, BaseSQLModel


class UserRole(str, Enum):
    """Роли пользователей"""

    ADMIN = 'admin'
    STUDENT = 'student'
    TEACHER = 'teacher'


class User(BaseSQLModel, table=True):
    __tablename__ = 'users'

    email: str = SQLField(unique=True, index=True, max_length=255, nullable=False)
    hashed_password: str = SQLField(nullable=False)
    first_name: str = SQLField(max_length=100, nullable=False)
    last_name: str = SQLField(max_length=100, nullable=False)
    role: UserRole = SQLField(default=UserRole.STUDENT, nullable=False)

    programs: list['Program'] = Relationship(back_populates='user', cascade_delete=True)
    courses: list['Course'] = Relationship(back_populates='user', cascade_delete=True)
    progress: list['UserProgress'] = Relationship(
        back_populates='user', cascade_delete=True
    )
    career_tracks: list['CareerTrack'] = Relationship(
        back_populates='user', cascade_delete=True
    )


class UserCreate(BaseSchema):
    """Схема для регистрации пользователя"""

    email: EmailStr = Field(..., max_length=255)
    password: str = Field(..., min_length=6, max_length=128)
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    role: UserRole = Field(default=UserRole.STUDENT)


class UserUpdate(BaseSchema):
    """Схема для обновления пользователя"""

    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    role: Optional[UserRole] = Field(None)


class LoginRequest(BaseSchema):
    """Схема для входа в систему"""

    email: EmailStr
    password: str


class UserPublic(BaseModelSchema):
    """Публичная информация о пользователе (наследует id, created_at, updated_at)"""

    email: EmailStr
    first_name: str
    last_name: str
    role: UserRole

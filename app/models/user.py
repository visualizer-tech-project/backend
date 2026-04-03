from enum import Enum
from typing import Optional

from pydantic import EmailStr
from sqlmodel import Field
from sqlmodel import Relationship

from app.models.base import BaseModelSchema, BaseSchema, BaseSQLModel



class UserRole(str, Enum):
    ADMIN = 'admin'
    STUDENT = 'student'
    TEACHER = 'teacher'


class User(BaseSQLModel, table=True):
    __tablename__ = 'users'

    email: str = Field(unique=True, index=True, max_length=255, nullable=False)
    hashed_password: str = Field(nullable=False)
    first_name: str = Field(max_length=100, nullable=False)
    last_name: str = Field(max_length=100, nullable=False)
    role: UserRole = Field(default=UserRole.STUDENT, nullable=False)

    programs: list['Program'] = Relationship(back_populates='user', cascade_delete=True)
    courses: list['Course'] = Relationship(back_populates='user', cascade_delete=True)
    progress: list['UserProgress'] = Relationship(back_populates='user', cascade_delete=True)
    career_tracks: list['CareerTrack'] = Relationship(back_populates='user', cascade_delete=True)



class UserCreate(BaseSchema):
    """Для создания пользователя"""
    email: EmailStr = Field(..., max_length=255)
    password: str = Field(..., min_length=6, max_length=128)
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    role: UserRole = Field(default=UserRole.STUDENT)


class UserUpdate(BaseSchema):
    """Для обновления пользователя"""
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    role: Optional[UserRole] = Field(None)


class UserPublic(BaseModelSchema):
    """Публичный ответ о пользователе"""
    email: EmailStr
    first_name: str
    last_name: str
    role: UserRole
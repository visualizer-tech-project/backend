from enum import Enum
from typing import TYPE_CHECKING, Optional
from pydantic import EmailStr
from sqlmodel import Field, Relationship
from app.core.constants import NAME_FIELD_CONFIG  # если вынесли в константы
from app.models.base import BaseSQLModel, BaseSchema, BaseModelSchema

if TYPE_CHECKING:
    from app.models.program import Program
    from app.models.course import Course
    from app.models.userprogress import UserProgress
    from app.models.careertrack import CareerTrack


class UserRole(str, Enum):
    ADMIN = 'admin'
    STUDENT = 'student'
    TEACHER = 'teacher'


class UserBase(BaseSchema):
    email: EmailStr = Field(..., max_length=255)
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    role: UserRole = Field(default=UserRole.STUDENT)


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


class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=128)


class UserUpdate(BaseSchema):
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    role: Optional[UserRole] = None


class UserPublic(UserBase, BaseModelSchema):
    pass
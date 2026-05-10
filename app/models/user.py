from enum import Enum
from typing import TYPE_CHECKING, List, Optional

from pydantic import EmailStr
from sqlmodel import Field, Relationship

from app.models.base import BaseSQLModel, BaseSchema, BaseModelSchema
from app.models.role import UserRoleMapping

if TYPE_CHECKING:
    from app.models.program import Program
    from app.models.course import Course
    from app.models.userprogress import UserProgress
    from app.models.careertrack import CareerTrack
    from app.models.role import Role
    from app.models.email import EmailNotification


class UserRole(str, Enum):
    ADMIN = 'admin'
    STUDENT = 'student'
    TEACHER = 'teacher'


class AccountStatus(str, Enum):
    CREATED = 'created'
    CONFIRMED = 'confirmed'
    BLOCKED = 'blocked'


class UserBase(BaseSchema):
    email: EmailStr = Field(max_length=255, unique=True, index=True)
    first_name: str = Field(max_length=100)
    last_name: str = Field(max_length=100)
    role: UserRole = Field(default=UserRole.STUDENT)
    status: AccountStatus = Field(default=AccountStatus.CREATED)


class User(UserBase, BaseSQLModel, table=True):
    __tablename__ = 'users'

    hashed_password: str = Field(nullable=False)

    programs: list['Program'] = Relationship(back_populates='user', cascade_delete=True)
    courses: list['Course'] = Relationship(back_populates='user', cascade_delete=True)
    progress: list['UserProgress'] = Relationship(
        back_populates='user', cascade_delete=True
    )
    career_tracks: list['CareerTrack'] = Relationship(
        back_populates='user', cascade_delete=True
    )

    roles: List['Role'] = Relationship(
        back_populates='users',
        link_model=UserRoleMapping,
        sa_relationship_kwargs={'lazy': 'selectin'},
    )

    email_notifications: List['EmailNotification'] = Relationship(
        back_populates='user',
        sa_relationship_kwargs={'lazy': 'selectin'},
    )


class UserCreate(UserBase):
    hashed_password: str = Field(..., min_length=6, max_length=128)


class UserUpdate(BaseSchema):
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    role: Optional[UserRole] = None
    status: Optional[AccountStatus] = None


class UserPublic(UserBase, BaseModelSchema):
    pass

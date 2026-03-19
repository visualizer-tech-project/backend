from enum import Enum
from typing import TYPE_CHECKING, List

from sqlmodel import Field, Relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.careertrack import CareerTrack
    from app.models.course import Course
    from app.models.program import Program
    from app.models.userprogress import UserProgress


class UserRole(str, Enum):
    ADMIN = 'admin'
    STUDENT = 'student'
    TEACHER = 'teacher'


class User(BaseModel, table=True):
    __tablename__ = 'users'

    email: str = Field(unique=True, index=True, max_length=255, nullable=False)
    hashed_password: str = Field(nullable=False)
    first_name: str = Field(max_length=100, nullable=False)
    last_name: str = Field(max_length=100, nullable=False)
    role: UserRole = Field(default=UserRole.STUDENT, nullable=False)

    programs: List['Program'] = Relationship(
        back_populates='user',
        sa_relationship_kwargs={'cascade': 'all, delete-orphan'}
    )
    courses: List['Course'] = Relationship(
        back_populates='user',
        sa_relationship_kwargs={'cascade': 'all, delete-orphan'}
    )
    progress: List['UserProgress'] = Relationship(
        back_populates='user',
        sa_relationship_kwargs={'cascade': 'all, delete-orphan'}
    )
    career_tracks: List['CareerTrack'] = Relationship(
        back_populates='user',
        sa_relationship_kwargs={'cascade': 'all, delete-orphan'}
    )

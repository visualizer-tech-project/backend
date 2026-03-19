from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Optional

from sqlmodel import Column, Field, Numeric, Relationship, UniqueConstraint

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.course import Course
    from app.models.user import User


class UserProgressStatus(str, Enum):
    NOT_STARTED = 'not_started'
    IN_PROGRESS = 'in_progress'
    COMPLETED = 'completed'


class UserProgress(BaseModel, table=True):
    __tablename__ = 'user_progress'
    __table_args__ = (UniqueConstraint('user_id', 'course_id', name='uq_user_course'),)

    user_id: int = Field(foreign_key='users.id', nullable=False, index=True)
    course_id: int = Field(foreign_key='courses.id', nullable=False, index=True)
    status: UserProgressStatus = Field(
        default=UserProgressStatus.NOT_STARTED, nullable=False
    )
    grade: Optional[float] = Field(
        default=None, sa_column=Column(Numeric(5, 2), nullable=True)
    )
    started_at: Optional[datetime] = Field(default=None, nullable=True)
    completed_at: Optional[datetime] = Field(default=None, nullable=True)

    user: 'User' = Relationship(back_populates='progress')
    course: 'Course' = Relationship(back_populates='progress')

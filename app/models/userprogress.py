from datetime import datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING, Optional

from pydantic import model_validator
from sqlmodel import Field, Relationship, UniqueConstraint

from app.models.base import BaseSQLModel, BaseSchema, BaseModelSchema

if TYPE_CHECKING:
    from app.models.course import Course
    from app.models.user import User


class ProgressStatus(str, Enum):
    NOT_STARTED = 'not_started'
    IN_PROGRESS = 'in_progress'
    COMPLETED = 'completed'


class UserProgress(BaseSQLModel, table=True):
    __tablename__ = 'user_progress'
    __table_args__ = (UniqueConstraint('user_id', 'course_id', name='uq_user_course'),)

    user_id: int = Field(foreign_key='users.id', nullable=False, index=True)
    course_id: int = Field(foreign_key='courses.id', nullable=False, index=True)
    status: ProgressStatus = Field(default=ProgressStatus.NOT_STARTED, nullable=False)
    grade: Optional[int] = Field(default=None, nullable=True, ge=0, le=100)
    started_at: Optional[datetime] = Field(default=None, nullable=True)
    completed_at: Optional[datetime] = Field(default=None, nullable=True)

    user: 'User' = Relationship(back_populates='progress')
    course: 'Course' = Relationship(back_populates='progress')

    @classmethod
    def create_with_defaults(
            cls,
            user_id: int,
            course_id: int,
            status: ProgressStatus,
            grade: Optional[int] = None,
            started_at: Optional[datetime] = None,
            completed_at: Optional[datetime] = None,
    ) -> 'UserProgress':
        now = datetime.now(timezone.utc)

        if started_at is None and status == ProgressStatus.IN_PROGRESS:
            started_at = now
        elif started_at is None and status == ProgressStatus.COMPLETED:
            started_at = now
            if completed_at is None:
                completed_at = now

        return cls(
            user_id=user_id,
            course_id=course_id,
            status=status,
            grade=grade,
            started_at=started_at,
            completed_at=completed_at,
        )

    def update_status_with_dates(self, new_status: ProgressStatus) -> None:
        now = datetime.now(timezone.utc)

        self.status = new_status

        if new_status == ProgressStatus.IN_PROGRESS and self.started_at is None:
            self.started_at = now
        elif new_status == ProgressStatus.COMPLETED:
            if self.started_at is None:
                self.started_at = now
            if self.completed_at is None:
                self.completed_at = now


class ProgressBase(BaseSchema):
    status: ProgressStatus
    grade: Optional[int] = Field(None, ge=0, le=100)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    @model_validator(mode='after')
    def validate_dates(self) -> 'ProgressBase':
        if self.started_at and self.completed_at and self.completed_at < self.started_at:
            raise ValueError('completed_at не может быть раньше started_at')
        return self

class ProgressUpdate(BaseSchema):
    status: Optional[ProgressStatus] = None
    grade: Optional[int] = Field(None, ge=0, le=100)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    @model_validator(mode='after')
    def validate_dates(self) -> 'ProgressUpdate':
        if self.started_at and self.completed_at and self.completed_at < self.started_at:
            raise ValueError('completed_at не может быть раньше started_at')
        return self

class ProgressUserCourseBase(BaseSchema):
    user_id: int = Field(foreign_key="users.id")
    course_id: int = Field(foreign_key="courses.id")

class ProgressCreate(ProgressBase, ProgressUserCourseBase):
    pass

class UserProgressPublic(ProgressBase, BaseModelSchema, ProgressUserCourseBase):
    pass

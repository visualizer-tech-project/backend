from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Optional

from pydantic import Field, model_validator
from sqlmodel import Field as SQLField
from sqlmodel import Relationship, UniqueConstraint

from app.models.base import BaseModelSchema, BaseSchema, BaseSQLModel

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

    user_id: int = SQLField(foreign_key='users.id', nullable=False, index=True)
    course_id: int = SQLField(foreign_key='courses.id', nullable=False, index=True)
    status: ProgressStatus = SQLField(
        default=ProgressStatus.NOT_STARTED, nullable=False
    )
    grade: Optional[int] = SQLField(default=None, nullable=True, ge=0, le=100)
    started_at: Optional[datetime] = SQLField(default=None, nullable=True)
    completed_at: Optional[datetime] = SQLField(default=None, nullable=True)

    user: 'User' = Relationship(back_populates='progress')
    course: 'Course' = Relationship(back_populates='progress')


class ProgressCreate(BaseSchema):
    """Схема для создания записи прогресса"""

    user_id: int
    course_id: int
    status: ProgressStatus
    grade: Optional[int] = Field(None, ge=0, le=100)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    @model_validator(mode='after')
    def validate_dates(self) -> 'ProgressCreate':
        if (
            self.started_at
            and self.completed_at
            and self.completed_at < self.started_at
        ):
            raise ValueError('completed_at не может быть раньше started_at')
        return self


class ProgressUpdate(BaseSchema):
    """Схема для обновления прогресса"""

    status: Optional[ProgressStatus] = None
    grade: Optional[int] = Field(None, ge=0, le=100)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    @model_validator(mode='after')
    def validate_dates(self) -> 'ProgressCreate':
        if (
            self.started_at
            and self.completed_at
            and self.completed_at < self.started_at
        ):
            raise ValueError('completed_at не может быть раньше started_at')
        return self


class UserProgressPublic(BaseModelSchema):
    """Публичная информация о прогрессе"""

    user_id: int
    course_id: int
    status: ProgressStatus
    grade: Optional[int] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class UserProgressWithDetails(UserProgressPublic):
    """Прогресс с деталями курса и пользователя"""

    course_title: Optional[str] = None
    course_type: Optional[str] = None
    program_id: Optional[int] = None
    user_name: Optional[str] = None
    user_email: Optional[str] = None

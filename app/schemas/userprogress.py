from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import Field

from app.schemas.base import BaseModelSchema, BaseSchema


class ProgressStatus(str, Enum):
    """Статус прогресса"""

    NOT_STARTED = 'not_started'
    IN_PROGRESS = 'in_progress'
    COMPLETED = 'completed'


class ProgressCreate(BaseSchema):
    """Схема для создания записи прогресса"""

    status: ProgressStatus = Field(..., description='Статус прохождения')
    grade: Optional[int] = Field(None, ge=0, le=100, description='Оценка')
    started_at: Optional[datetime] = Field(None, description='Дата начала')
    completed_at: Optional[datetime] = Field(None, description='Дата завершения')


class ProgressUpdate(BaseSchema):
    """Схема для обновления прогресса"""

    status: Optional[ProgressStatus] = Field(None, description='Статус прохождения')
    grade: Optional[int] = Field(None, ge=0, le=100, description='Оценка')
    started_at: Optional[datetime] = Field(None, description='Дата начала')
    completed_at: Optional[datetime] = Field(None, description='Дата завершения')


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
    course_semester: Optional[int] = None
    user_name: Optional[str] = None

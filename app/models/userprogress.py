import datetime
from enum import Enum
from typing import Optional, TYPE_CHECKING
from sqlmodel import Column, Field, Numeric, Relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.course import Course
    from app.models.user import User

class UserProgressStatus(str, Enum):
    NOT_STARTED = 'not_started'
    IN_PROCESS = 'in_process'
    FINISHED = 'finished'

class UserProgress(BaseModel, table=True):
    __tablename__ = 'user_progress'

    user_id: int = Field(foreign_key='users.id')
    course_id: int = Field(foreign_key='courses.id')
    progress: UserProgressStatus
    grade: Optional[float] = Field(default=None, sa_column=Column(Numeric(5, 2)))
    started_at: Optional[datetime.datetime] = None
    completed_at: Optional[datetime.datetime] = None

    user: 'User' = Relationship(back_populates='progress')
    course: 'Course' = Relationship(back_populates='progress')
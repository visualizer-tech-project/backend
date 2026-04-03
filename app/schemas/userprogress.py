from typing import Optional

from app.models.base import BaseSchema
from app.models.userprogress import UserProgressPublic


class UserProgressWithDetails(BaseSchema):
    """Составная схема: прогресс с деталями курса и пользователя"""
    progress: UserProgressPublic
    course_title: Optional[str] = None
    course_type: Optional[str] = None
    program_id: Optional[int] = None
    user_name: Optional[str] = None
    user_email: Optional[str] = None
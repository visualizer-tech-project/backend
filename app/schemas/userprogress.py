from typing import Optional, Any
from pydantic import computed_field, Field
from app.models.base import BaseSchema
from app.models.userprogress import UserProgressPublic


class UserProgressWithDetails(BaseSchema):
    """Составная схема: прогресс с деталями курса и пользователя"""

    progress: UserProgressPublic

    course: Optional[Any] = Field(None, exclude=True)
    user: Any = Field(exclude=True)

    @computed_field
    @property
    def course_title(self) -> Optional[str]:
        return self.course.title if self.course else None

    @computed_field
    @property
    def course_type(self) -> Optional[str]:
        if self.course and hasattr(self.course, 'type') and self.course.type:
            return getattr(self.course.type, 'value', self.course.type)
        return None

    @computed_field
    @property
    def program_id(self) -> Optional[int]:
        return self.course.program_id if self.course else None

    @computed_field
    @property
    def user_name(self) -> str:
        return f'{self.user.first_name} {self.user.last_name}'

    @computed_field
    @property
    def user_email(self) -> str:
        return self.user.email
